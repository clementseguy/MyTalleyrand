#!/usr/bin/env python3
"""Point d'entrée principal de l'application Talleyrand Coach."""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

from src.coach import CoachingEngine
from src.config import load_config, validate_config
from src.llm_client import LLMClient
from src.overlay import TalleyrandOverlay
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
    parser.add_argument(
        "--victory-focus",
        default="science",
        choices=["domination", "science", "culture", "diplomatie", "équilibrée"],
        help="objectif de victoire (phase 4)",
    )
    args = parser.parse_args()

    config = load_config()
    _configure_logging(config.log_file)

    errors = validate_config(config)
    if errors:
        for error in errors:
            logger.error("Configuration invalide: %s", error)
        return 1

    history_file = config.export_dir / "coach_history.json"
    overlay_state_file = config.export_dir / "overlay_state.json"

    overlay = TalleyrandOverlay(state_file=overlay_state_file)

    llm_client = LLMClient(
        provider=config.llm_provider,
        model=config.llm_model,
        timeout_seconds=config.llm_timeout_seconds,
        max_tokens=config.llm_max_tokens,
        temperature=config.llm_temperature,
        system_prompt=config.llm_system_prompt,
        user_prompt_template=config.llm_user_prompt_template,
        api_key=config.llm_api_key,
        status_callback=lambda status: overlay.show_status(status.title, status.message, status.suggestion),
    )
    coaching_engine = CoachingEngine(llm_client=llm_client, history_file=history_file)
    coaching_engine.set_victory_focus(args.victory_focus)

    def on_new_turn(payload: dict, source_file: Path) -> None:
        logger.info(
            "✅ Tour ingéré depuis %s (turn_id=%s, turn_number=%s)",
            source_file,
            payload["turn_id"],
            payload["turn_number"],
        )
        advice = coaching_engine.maybe_generate_advice(payload)
        if advice is not None:
            overlay.show_advice(advice)

    def on_gamestate_issue(issue: GameStateIssue, source_file: Path) -> None:
        logger.warning("Problème gamestate détecté depuis %s: %s", source_file, issue.message)
        overlay.show_status("Problème gamestate", issue.message, issue.suggestion)

    logger.info("🎮 Démarrage de Talleyrand Coach...")
    logger.info("✅ Configuration chargée (schema=%s)", config.schema_version)
    logger.info("📁 Surveillance prévue: %s", config.gamestate_file)

    watcher = GameStateWatcher(config.gamestate_file, on_new_turn, issue_callback=on_gamestate_issue)
    watcher.start()

    if args.once:
        time.sleep(0.6)
        watcher.stop()
        logger.info("Mode --once terminé")
        return 0

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("⏹️ Arrêt de Talleyrand Coach")
    finally:
        watcher.stop()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
