"""Surveillance du fichier gamestate.json exporté par le mod."""

from __future__ import annotations

import json
import logging
import threading
import time
from pathlib import Path
from typing import Any, Callable

from src.gamestate_schema import validate_gamestate

logger = logging.getLogger(__name__)


class GameStateWatcher:
    """Surveille gamestate.json, valide son contenu et déduplique par turn_id."""

    def __init__(
        self,
        gamestate_file: Path,
        callback: Callable[[dict[str, Any], Path], None],
        poll_interval_seconds: float = 0.5,
    ):
        self.gamestate_file = gamestate_file
        self.callback = callback
        self.poll_interval_seconds = poll_interval_seconds
        self._seen_turn_ids: set[int] = set()
        self._last_mtime_ns: int | None = None
        self._running = False
        self._thread: threading.Thread | None = None

        logger.info("👁️ GameStateWatcher initialisé sur %s", gamestate_file)

    def start(self) -> None:
        """Démarre la boucle de surveillance en arrière-plan."""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._run, name="gamestate-watcher", daemon=True)
        self._thread.start()
        logger.info("▶️ Surveillance démarrée (intervalle=%.2fs)", self.poll_interval_seconds)

    def stop(self) -> None:
        """Arrête la surveillance et attend la fin du thread."""
        if not self._running:
            return

        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=2)
            self._thread = None
        logger.info("⏹️ Surveillance arrêtée")

    def _run(self) -> None:
        while self._running:
            try:
                self._check_for_update()
            except Exception:
                logger.exception("Erreur inattendue pendant la surveillance")
            time.sleep(self.poll_interval_seconds)

    def _check_for_update(self) -> None:
        if not self.gamestate_file.exists():
            return

        stat = self.gamestate_file.stat()
        if self._last_mtime_ns == stat.st_mtime_ns:
            return

        self._last_mtime_ns = stat.st_mtime_ns

        try:
            payload = json.loads(self.gamestate_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            logger.warning("JSON corrompu ou incomplet (%s): %s", self.gamestate_file, exc)
            return

        errors = validate_gamestate(payload)
        if errors:
            details = ", ".join(f"{err.field}: {err.message}" for err in errors)
            logger.warning("gamestate.json invalide ignoré: %s", details)
            return

        turn_id = payload["turn_id"]
        if turn_id in self._seen_turn_ids:
            logger.debug("Tour %s déjà traité, ignoré", turn_id)
            return

        self._seen_turn_ids.add(turn_id)
        logger.info("🧭 Nouveau tour détecté: turn_id=%s turn_number=%s", turn_id, payload["turn_number"])
        self.callback(payload, self.gamestate_file)
