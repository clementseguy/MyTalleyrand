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
from src.gamestate_source import FileGameStateSource, GameStateSource

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GameStateIssue:
    """Problème détecté pendant la surveillance de gamestate.json."""

    kind: str
    message: str
    suggestion: str


class GameStateWatcher:
    """Surveille une source de gamestate, valide son contenu et déduplique par turn_id.

    La source peut être un fichier JSON (Windows) ou une base SQLite ModUserData
    (macOS). Le watcher ne connaît que l'interface GameStateSource ; la logique de
    détection de changement, validation de schéma et déduplication reste identique.
    """

    def __init__(
        self,
        gamestate_file: Path,
        callback: Callable[[dict[str, Any], Path], None],
        poll_interval_seconds: float = 0.5,
        issue_callback: Callable[[GameStateIssue, Path], None] | None = None,
        source: GameStateSource | None = None,
    ):
        self.gamestate_file = gamestate_file
        self.callback = callback
        self.poll_interval_seconds = poll_interval_seconds
        self.issue_callback = issue_callback
        # Par défaut (compat ascendante) : surveillance d'un fichier JSON.
        self.source: GameStateSource = source or FileGameStateSource(gamestate_file)
        self._seen_turn_ids: set[int] = set()
        self._last_change_token: int | None = None
        self._last_issue_signature: tuple[str, str] | None = None
        self._last_seen_exists = False
        self._running = False
        self._thread: threading.Thread | None = None

        logger.info("👁️ GameStateWatcher initialisé sur %s", self.source.label)

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
        snapshot = self.source.read()

        if not snapshot.exists:
            self._last_seen_exists = False
            self._notify_issue(
                GameStateIssue(
                    kind="missing",
                    message=f"Source de gamestate introuvable ({self.source.label}).",
                    suggestion="Vérifiez que le mod MyTalleyrand est activé et qu'une partie a démarré.",
                )
            )
            return

        # Rien de neuf (contenu inchangé, ou source présente mais pas encore de gamestate).
        if snapshot.change_token is None or snapshot.change_token == self._last_change_token:
            return
        if snapshot.raw_json is None:
            return

        self._last_change_token = snapshot.change_token
        raw_content = snapshot.raw_json
        if not self._last_seen_exists:
            logger.info("📄 Gamestate détecté: %s (%d octets)", self.source.label, len(raw_content))
        else:
            logger.info("🔄 Gamestate mis à jour: %s (%d octets)", self.source.label, len(raw_content))
        self._last_seen_exists = True

        try:
            if not raw_content.strip():
                raise json.JSONDecodeError("empty content", raw_content, 0)
            payload = json.loads(raw_content)
        except json.JSONDecodeError as exc:
            logger.warning("JSON corrompu ou incomplet (%s): %s", self.source.label, exc)
            self._notify_issue(
                GameStateIssue(
                    kind="invalid_json",
                    message="Le gamestate est vide, incomplet ou corrompu.",
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
