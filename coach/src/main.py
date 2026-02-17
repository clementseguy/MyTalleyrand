#!/usr/bin/env python3
"""Point d'entrée principal de l'application Talleyrand Coach."""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

from src.config import load_config, validate_config
from src.watcher import GameStateWatcher

logger = logging.getLogger(__name__)


def _configure_logging(log_file: Path) -> None:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
    )


def _on_new_turn(payload: dict, source_file: Path) -> None:
    logger.info(
        "✅ Tour ingéré depuis %s (turn_id=%s, turn_number=%s)",
        source_file,
        payload["turn_id"],
        payload["turn_number"],
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Talleyrand Coach")
    parser.add_argument("--once", action="store_true", help="démarre puis s'arrête")
    args = parser.parse_args()

    config = load_config()
    _configure_logging(config.log_file)

    errors = validate_config(config)
    if errors:
        for error in errors:
            logger.error("Configuration invalide: %s", error)
        return 1

    logger.info("🎮 Démarrage de Talleyrand Coach...")
    logger.info("✅ Configuration chargée (schema=%s)", config.schema_version)
    logger.info("📁 Surveillance prévue: %s", config.gamestate_file)

    watcher = GameStateWatcher(config.gamestate_file, _on_new_turn)
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
