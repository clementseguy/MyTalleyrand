#!/usr/bin/env python3
"""Point d'entrée principal de l'application Talleyrand Coach."""

from __future__ import annotations

import argparse
import logging
import os
import sys
import time
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.coach import CoachingEngine
from src.config import (
    ConfigError,
    DEFAULT_SETTINGS_PATH,
    DEFAULT_USER_SETTINGS_PATH,
    SUPPORTED_LLM_PROVIDERS,
    load_config,
    validate_config,
)
from src.llm_client import LLMClient
from src.onboarding import (
    build_onboarding_checks,
    format_onboarding_report,
    mark_onboarding_done,
    should_run_first_launch_onboarding,
)
from src.gamestate_source import build_source
from src.overlay import OverlaySettings, TalleyrandOverlay
from src.preferences import PreferencesStore, VICTORY_FOCUSES
from src.watcher import GameStateIssue, GameStateWatcher

logger = logging.getLogger(__name__)


def _configure_logging(log_file: Path) -> None:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Talleyrand Coach")
    parser.add_argument("--once", action="store_true", help="démarre puis s'arrête")
    parser.add_argument("--onboarding", action="store_true", help="affiche les vérifications de premier lancement puis s'arrête")
    parser.add_argument(
        "--llm-provider",
        choices=SUPPORTED_LLM_PROVIDERS,
        default=None,
        help="provider LLM à utiliser pour ce lancement (mistral par défaut, openai disponible)",
    )
    parser.add_argument(
        "--llm-model",
        default=None,
        help="modèle LLM à utiliser pour ce lancement",
    )
    parser.add_argument(
        "--victory-focus",
        default=None,
        choices=VICTORY_FOCUSES,
        help="objectif de victoire (phase 4)",
    )
    args = parser.parse_args()
    if args.llm_provider is not None:
        os.environ["TALLEYRAND_LLM_PROVIDER"] = args.llm_provider
    if args.llm_model is not None:
        os.environ["TALLEYRAND_LLM_MODEL"] = args.llm_model

    try:
        config = load_config()
    except ConfigError as exc:
        logging.basicConfig(level=logging.ERROR, format="%(levelname)s - %(message)s")
        logger.error("Configuration invalide: %s", exc)
        return 1

    _configure_logging(config.log_file)

    errors = validate_config(config)
    if errors:
        for error in errors:
            logger.error("Configuration invalide: %s", error)
        return 1

    history_file = config.export_dir / "coach_history.json"
    overlay_state_file = config.export_dir / "overlay_state.json"
    preferences_file = config.export_dir / "user_preferences.json"

    overlay = TalleyrandOverlay(
        state_file=overlay_state_file,
        settings=OverlaySettings(
            width=config.overlay_width,
            height=config.overlay_height,
            opacity=config.overlay_opacity,
        ),
        enable_qt=not args.once and not args.onboarding,
    )

    llm_client = LLMClient(
        provider=config.llm_provider,
        model=config.llm_model,
        timeout_seconds=config.llm_timeout_seconds,
        max_tokens=config.llm_max_tokens,
        temperature=config.llm_temperature,
        system_prompt=config.llm_system_prompt,
        user_prompt_template=config.llm_user_prompt_template,
        detail_level=config.llm_detail_level,
        api_key=config.llm_api_key,
        status_callback=lambda status: overlay.show_status(status.title, status.message, status.suggestion),
    )
    preferences_store = PreferencesStore(preferences_file)
    coaching_engine = CoachingEngine(
        llm_client=llm_client,
        history_file=history_file,
        preferences_store=preferences_store,
        analysis_interval_turns=config.analysis_interval_turns,
        cost_limit_usd=config.cost_limit_usd,
    )
    if args.victory_focus is not None:
        coaching_engine.set_victory_focus(args.victory_focus)

    def prompt_victory_focus() -> None:
        selected_focus = overlay.request_victory_focus(coaching_engine.victory_focus)
        if selected_focus:
            coaching_engine.set_victory_focus(selected_focus)
            overlay.show_status(
                "Stratégie mise à jour",
                f"Objectif de victoire: {coaching_engine.victory_focus}.",
                "Le changement sera pris en compte dès la prochaine analyse.",
                critical=False,
            )

    overlay.set_preferences_callback(prompt_victory_focus)

    def run_onboarding(force: bool = False) -> None:
        checks = build_onboarding_checks(config)
        report = format_onboarding_report(checks)
        logger.info("%s", report)
        failed = [check for check in checks if not check.ok]
        if failed or force:
            overlay.show_status(
                "Vérification premier lancement",
                "\n".join(f"{'✅' if check.ok else '⚠️'} {check.name}" for check in checks),
                failed[0].suggestion if failed else "Tous les prérequis vérifiables sont prêts.",
                critical=bool(failed),
            )
        mark_onboarding_done(config)

    if args.onboarding:
        run_onboarding(force=True)
        return 0
    if not args.once and should_run_first_launch_onboarding(config):
        run_onboarding()

    watched_config_files = [DEFAULT_SETTINGS_PATH, DEFAULT_USER_SETTINGS_PATH]
    last_config_mtime = max((path.stat().st_mtime_ns for path in watched_config_files if path.exists()), default=0)

    def refresh_runtime_budget_settings() -> None:
        nonlocal last_config_mtime
        current_mtime = max((path.stat().st_mtime_ns for path in watched_config_files if path.exists()), default=0)
        if current_mtime <= last_config_mtime:
            return
        try:
            refreshed = load_config()
        except ConfigError as exc:
            logger.warning("Configuration runtime ignorée: %s", exc)
            return
        errors = validate_config(refreshed)
        if errors:
            logger.warning("Configuration runtime ignorée: %s", "; ".join(errors))
            return
        last_config_mtime = current_mtime
        coaching_engine.update_runtime_settings(refreshed.analysis_interval_turns, refreshed.cost_limit_usd)
        llm_client.detail_level = refreshed.llm_detail_level
        logger.info("Réglages budget rechargés: intervalle=%s, détail=%s, plafond=$%.2f", refreshed.analysis_interval_turns, refreshed.llm_detail_level, refreshed.cost_limit_usd)

    def on_new_turn(payload: dict, source_file: Path) -> None:
        logger.info(
            "✅ Tour ingéré depuis %s (turn_id=%s, turn_number=%s)",
            source_file,
            payload["turn_id"],
            payload["turn_number"],
        )
        refresh_runtime_budget_settings()
        if payload["turn_number"] == 1 and not args.once:
            try:
                # Demander le focus de victoire sur le thread UI de l'overlay
                overlay._dispatch_backend(prompt_victory_focus)
            except Exception:
                # En cas d'erreur, retomber sur l'appel synchrone (sécurisé pour backend texte)
                logger.exception("Échec du dispatch UI pour prompt_victory_focus, tentative synchrone")
                try:
                    prompt_victory_focus()
                except Exception:
                    logger.exception("Échec de prompt_victory_focus")
        advice = coaching_engine.maybe_generate_advice(payload)
        if advice is not None:
            overlay.show_advice(advice, budget_status=coaching_engine.get_budget_status())

    def on_gamestate_issue(issue: GameStateIssue, source_file: Path) -> None:
        logger.warning("Problème gamestate détecté depuis %s: %s", source_file, issue.message)
        overlay.show_status("Problème gamestate", issue.message, issue.suggestion)

    # Sélection de la source selon la plateforme :
    #  - 'sqlite' (défaut macOS) : base ModUserData écrite par le mod (pas de io côté Lua).
    #  - 'file'  : fichier gamestate.json (mod Windows).
    if config.gamestate_source == "sqlite":
        watch_path = config.gamestate_db
    else:
        watch_path = config.gamestate_file
    source = build_source(
        config.gamestate_source,
        db_path=config.gamestate_db,
        file_path=config.gamestate_file,
    )

    logger.info("🎮 Démarrage de Talleyrand Coach...")
    logger.info("✅ Configuration chargée (schema=%s)", config.schema_version)
    logger.info("📁 Surveillance (%s): %s", config.gamestate_source, watch_path)

    watcher = GameStateWatcher(
        watch_path,
        on_new_turn,
        issue_callback=on_gamestate_issue,
        source=source,
    )
    watcher.start()

    if args.once:
        time.sleep(0.6)
        watcher.stop()
        logger.info("Mode --once terminé")
        return 0

    try:
        # Bloquant : boucle d'événements Qt (backend graphique) ou veille (texte).
        # Sans cette boucle, la fenêtre overlay ne s'affiche jamais.
        overlay.run_forever()
    except KeyboardInterrupt:
        logger.info("⏹️ Arrêt de Talleyrand Coach")
    finally:
        watcher.stop()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
