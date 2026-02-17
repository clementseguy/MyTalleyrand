"""Overlay MVP (phase 3) avec persistance de position et masquage/affichage."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

from src.llm_client import LLMAdvice

logger = logging.getLogger(__name__)


@dataclass
class OverlayPosition:
    x: int = 30
    y: int = 30


class TalleyrandOverlay:
    """Abstraction UI testable sans dépendance graphique runtime."""

    def __init__(self, state_file: Path):
        self.state_file = state_file
        self.visible = True
        self.position = OverlayPosition()
        self.last_rendered_text = ""
        self._load_state()
        logger.info("🖼️ Overlay initialisé en (%s,%s)", self.position.x, self.position.y)

    def _load_state(self) -> None:
        if not self.state_file.exists():
            return
        payload = json.loads(self.state_file.read_text(encoding="utf-8"))
        self.position = OverlayPosition(x=int(payload.get("x", 30)), y=int(payload.get("y", 30)))
        self.visible = bool(payload.get("visible", True))

    def _save_state(self) -> None:
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        payload = {"x": self.position.x, "y": self.position.y, "visible": self.visible}
        self.state_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def move_to(self, x: int, y: int) -> None:
        self.position = OverlayPosition(x=x, y=y)
        self._save_state()

    def toggle_visibility(self) -> bool:
        self.visible = not self.visible
        self._save_state()
        return self.visible

    def show_advice(self, advice: LLMAdvice) -> None:
        lines = [
            f"Objectif (10 tours): {advice.objective_10_turns}",
            "Actions prioritaires:",
        ]
        lines.extend([f"- {action}" for action in advice.priority_actions])
        self.last_rendered_text = "\n".join(lines)
        logger.info("💬 Overlay mis à jour avec %s actions", len(advice.priority_actions))
