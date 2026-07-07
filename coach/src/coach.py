"""Logique de coaching (phase 4) : déclenchement, catégorisation et historique."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.llm_client import LLMAdvice, LLMClient
from src.preferences import PreferencesStore, UserPreferences, normalize_victory_focus

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CoachingDecision:
    should_analyze: bool
    reason: str


class CoachingEngine:
    """Orchestre les analyses de tour et persiste un historique minimal."""

    def __init__(
        self,
        llm_client: LLMClient,
        history_file: Path,
        preferences_store: PreferencesStore | None = None,
    ):
        self.llm_client = llm_client
        self.history_file = history_file
        self.preferences_store = preferences_store
        self.preferences = preferences_store.load() if preferences_store is not None else UserPreferences()
        self.victory_focus = self.preferences.normalized_focus()

    @staticmethod
    def get_decision(turn_number: int) -> CoachingDecision:
        if turn_number == 1:
            return CoachingDecision(True, "tour_1_initialisation")
        if turn_number % 10 == 0:
            return CoachingDecision(True, "cycle_10_tours")
        return CoachingDecision(False, "hors_cycle")

    def set_victory_focus(self, focus: str) -> None:
        self.victory_focus = normalize_victory_focus(focus)
        self.preferences.victory_focus = self.victory_focus
        if self.preferences_store is not None:
            self.preferences_store.save(self.preferences)

    def maybe_generate_advice(self, game_state: dict[str, Any]) -> LLMAdvice | None:
        turn_number = int(game_state["turn_number"])
        decision = self.get_decision(turn_number)

        if not decision.should_analyze:
            logger.info("⏭️ Pas d'analyse au tour %s (%s)", turn_number, decision.reason)
            return None

        if self.preferences_store is not None:
            self.preferences = self.preferences_store.update_from_game_state(game_state, self.preferences)
            self.victory_focus = self.preferences.normalized_focus()

        insufficient_context = self._detect_insufficient_context(game_state)
        if insufficient_context is not None:
            advice = insufficient_context
            self._append_history(game_state=game_state, advice=advice, reason="contexte_insuffisant")
            logger.info("🟡 Contexte insuffisant au tour %s", turn_number)
            return advice

        advice = self.llm_client.generate_advice(game_state, victory_focus=self._build_victory_context())
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
            "game_parameters": asdict(self.preferences.game_parameters),
            "advice": asdict(advice),
        }

        existing: list[dict[str, Any]] = []
        if self.history_file.exists():
            try:
                existing = json.loads(self.history_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, ValueError):
                logger.warning("Historique corrompu, réinitialisation")

        existing.append(entry)
        self.history_file.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")


    def _build_victory_context(self) -> str:
        params = self.preferences.game_parameters
        details = []
        if params.difficulty:
            details.append(f"difficulté {params.difficulty}")
        if params.map_size:
            details.append(f"carte {params.map_size}")
        if params.game_speed:
            details.append(f"vitesse {params.game_speed}")
        return self.victory_focus if not details else f"{self.victory_focus} ({', '.join(details)})"

    def _detect_insufficient_context(self, game_state: dict[str, Any]) -> LLMAdvice | None:
        player = game_state.get("player")
        cities = game_state.get("cities")
        units = game_state.get("units")
        reasons: list[str] = []
        if not isinstance(player, dict) or not player:
            reasons.append("identité du joueur absente")
        if cities is not None and isinstance(cities, list) and len(cities) == 0:
            reasons.append("aucune ville détectée")
        if cities is None and units is None and int(game_state.get("turn_number", 1)) <= 1:
            reasons.append("données villes/unités non encore exportées")
        if not reasons:
            return None
        return LLMAdvice(
            objective_10_turns="Compléter le contexte de partie avant de figer un plan stratégique.",
            priority_actions=[
                "Fonder ou sélectionner la capitale si ce n'est pas encore fait.",
                "Attendre le prochain export de tour pour inclure villes, unités et paramètres de partie.",
                "Vérifier que le mod MyTalleyrand exporte bien les sections détaillées du gamestate.",
            ],
            risks=["Conseils volontairement prudents car le contexte disponible est incomplet."],
            confidence=35,
            categories={"economie": [], "science": [], "militaire": [], "diplomatie": []},
            source="context_insufficient",
        )
