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
from src.watcher import GameStateWatcher

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

    llm_client = LLMClient(provider=config.llm_provider, model=config.llm_model)
    coaching_engine = CoachingEngine(llm_client=llm_client, history_file=history_file)
    coaching_engine.set_victory_focus(args.victory_focus)
    overlay = TalleyrandOverlay(state_file=overlay_state_file)

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

    logger.info("🎮 Démarrage de Talleyrand Coach...")
    logger.info("✅ Configuration chargée (schema=%s)", config.schema_version)
    logger.info("📁 Surveillance prévue: %s", config.gamestate_file)

    watcher = GameStateWatcher(config.gamestate_file, on_new_turn)
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
