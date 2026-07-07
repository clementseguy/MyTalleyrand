"""Surveillance du fichier gamestate.json exporté par le mod."""

from __future__ import annotations

import json
import logging
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from src.gamestate_schema import validate_gamestate

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GameStateIssue:
    """Problème détecté pendant la surveillance de gamestate.json."""

    kind: str
    message: str
    suggestion: str


class GameStateWatcher:
    """Surveille gamestate.json, valide son contenu et déduplique par turn_id."""

    def __init__(
        self,
        gamestate_file: Path,
        callback: Callable[[dict[str, Any], Path], None],
        poll_interval_seconds: float = 0.5,
        issue_callback: Callable[[GameStateIssue, Path], None] | None = None,
    ):
        self.gamestate_file = gamestate_file
        self.callback = callback
        self.poll_interval_seconds = poll_interval_seconds
        self.issue_callback = issue_callback
        self._seen_turn_ids: set[int] = set()
        self._last_mtime_ns: int | None = None
        self._last_issue_signature: tuple[str, str] | None = None
        self._last_seen_exists = False
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
            self._last_seen_exists = False
            self._notify_issue(
                GameStateIssue(
                    kind="missing",
                    message="gamestate.json est introuvable.",
                    suggestion="Vérifiez que le mod MyTalleyrand est activé et que le dossier export existe.",
                )
            )
            return

        stat = self.gamestate_file.stat()
        if self._last_mtime_ns == stat.st_mtime_ns:
            return

        self._last_mtime_ns = stat.st_mtime_ns
        if not self._last_seen_exists:
            logger.info("📄 Fichier gamestate détecté: %s (taille=%d octets)", self.gamestate_file, stat.st_size)
        else:
            logger.info("🔄 Fichier gamestate mis à jour: %s (taille=%d octets)", self.gamestate_file, stat.st_size)
        self._last_seen_exists = True

        try:
            raw_content = self.gamestate_file.read_text(encoding="utf-8")
            if not raw_content.strip():
                raise json.JSONDecodeError("empty file", raw_content, 0)
            payload = json.loads(raw_content)
        except json.JSONDecodeError as exc:
            logger.warning("JSON corrompu ou incomplet (%s): %s", self.gamestate_file, exc)
            self._notify_issue(
                GameStateIssue(
                    kind="invalid_json",
                    message="gamestate.json est vide, incomplet ou corrompu.",
                    suggestion="Attendez le prochain tour ou consultez Lua.log si le problème persiste.",
                )
            )
            return

        errors = validate_gamestate(payload)
        if errors:
            details = ", ".join(f"{err.field}: {err.message}" for err in errors)
            logger.warning("gamestate.json invalide ignoré: %s", details)
            self._notify_issue(
                GameStateIssue(
                    kind="invalid_schema",
                    message=f"gamestate.json ne respecte pas le schéma attendu: {details}.",
                    suggestion="Vérifiez la version du mod, les permissions du dossier MODS et Lua.log.",
                )
            )
            return

        self._last_issue_signature = None
        turn_id = payload["turn_id"]
        if turn_id in self._seen_turn_ids:
            logger.debug("Tour %s déjà traité, ignoré", turn_id)
            return

        self._seen_turn_ids.add(turn_id)
        logger.info("🧭 Nouveau tour détecté: turn_id=%s turn_number=%s", turn_id, payload["turn_number"])
        self.callback(payload, self.gamestate_file)

    def _notify_issue(self, issue: GameStateIssue) -> None:
        signature = (issue.kind, issue.message)
        if signature == self._last_issue_signature:
            return

        self._last_issue_signature = signature
        if self.issue_callback is not None:
            self.issue_callback(issue, self.gamestate_file)
