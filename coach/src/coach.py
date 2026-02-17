"""Logique de coaching (phase 4) : déclenchement, catégorisation et historique."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.llm_client import LLMAdvice, LLMClient

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CoachingDecision:
    should_analyze: bool
    reason: str


class CoachingEngine:
    """Orchestre les analyses de tour et persiste un historique minimal."""

    def __init__(self, llm_client: LLMClient, history_file: Path):
        self.llm_client = llm_client
        self.history_file = history_file
        self.victory_focus = "équilibrée"

    @staticmethod
    def get_decision(turn_number: int) -> CoachingDecision:
        if turn_number == 1:
            return CoachingDecision(True, "tour_1_initialisation")
        if turn_number % 10 == 0:
            return CoachingDecision(True, "cycle_10_tours")
        return CoachingDecision(False, "hors_cycle")

    def set_victory_focus(self, focus: str) -> None:
        self.victory_focus = focus

    def maybe_generate_advice(self, game_state: dict[str, Any]) -> LLMAdvice | None:
        turn_number = int(game_state["turn_number"])
        decision = self.get_decision(turn_number)

        if not decision.should_analyze:
            logger.info("⏭️ Pas d'analyse au tour %s (%s)", turn_number, decision.reason)
            return None

        advice = self.llm_client.generate_advice(game_state, victory_focus=self.victory_focus)
        self._append_history(game_state=game_state, advice=advice, reason=decision.reason)
        logger.info("🧠 Conseil généré pour le tour %s (%s)", turn_number, decision.reason)
        return advice

    def _append_history(self, game_state: dict[str, Any], advice: LLMAdvice, reason: str) -> None:
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "turn_id": game_state["turn_id"],
            "turn_number": game_state["turn_number"],
            "reason": reason,
            "victory_focus": self.victory_focus,
            "advice": asdict(advice),
        }

        existing: list[dict[str, Any]] = []
        if self.history_file.exists():
            existing = json.loads(self.history_file.read_text(encoding="utf-8"))

        existing.append(entry)
        self.history_file.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")
