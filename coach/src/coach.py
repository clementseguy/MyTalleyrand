"""Logique de coaching (phase 4) : déclenchement, catégorisation et historique."""

from __future__ import annotations

import hashlib
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
class BudgetStatus:
    total_cost_usd: float
    limit_usd: float
    threshold_reached: bool


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
        analysis_interval_turns: int = 10,
        cost_limit_usd: float = 2.0,
    ):
        self.llm_client = llm_client
        self.history_file = history_file
        self.preferences_store = preferences_store
        self.analysis_interval_turns = max(1, int(analysis_interval_turns))
        self.cost_limit_usd = max(0.01, float(cost_limit_usd))
        self.preferences = preferences_store.load() if preferences_store is not None else UserPreferences()
        self.victory_focus = self.preferences.normalized_focus()
        # Dernier tour réellement analysé, pour un déclenchement robuste aux tours sautés.
        self._last_analyzed_turn = 0

    def get_decision(self, turn_number: int) -> CoachingDecision:
        if turn_number == 1:
            return CoachingDecision(True, "tour_1_initialisation")
        interval = self.analysis_interval_turns
        # Analyse une fois par bloc de `interval` tours (bornes 10, 20, 30…). En
        # comparant les blocs plutôt que `turn % interval == 0`, un tour pile sur
        # la borne qui serait sauté (course d'écriture, tour manqué) est rattrapé
        # par le tour suivant du même bloc.
        if turn_number // interval > self._last_analyzed_turn // interval:
            return CoachingDecision(True, f"cycle_{interval}_tours")
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

        # Marque ce bloc comme analysé (évite une seconde analyse dans le même bloc).
        self._last_analyzed_turn = turn_number

        if self.preferences_store is not None:
            self.preferences = self.preferences_store.update_from_game_state(game_state, self.preferences)
            self.victory_focus = self.preferences.normalized_focus()

        self._archive_history_if_new_game(turn_number)

        insufficient_context = self._detect_insufficient_context(game_state)
        if insufficient_context is not None:
            advice = insufficient_context
            self._append_history(game_state=game_state, advice=advice, reason="contexte_insuffisant")
            logger.info("🟡 Contexte insuffisant au tour %s", turn_number)
            return advice

        cache_key = self._cache_key(game_state)
        cached = self._find_cached_advice(cache_key)
        if cached is not None:
            self._append_history(game_state=game_state, advice=cached, reason="cache_hit", cache_key=cache_key)
            logger.info("♻️ Conseil réutilisé depuis le cache pour le tour %s", turn_number)
            return cached

        advice = self.llm_client.generate_advice(game_state, victory_focus=self._build_victory_context())
        self._append_history(game_state=game_state, advice=advice, reason=decision.reason, cache_key=cache_key)
        logger.info("🧠 Conseil généré pour le tour %s (%s)", turn_number, decision.reason)
        return advice

    def _append_history(self, game_state: dict[str, Any], advice: LLMAdvice, reason: str, cache_key: str | None = None) -> None:
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "turn_id": game_state["turn_id"],
            "turn_number": game_state["turn_number"],
            "reason": reason,
            "victory_focus": self.victory_focus,
            "game_parameters": asdict(self.preferences.game_parameters),
            "cache_key": cache_key,
            "advice": asdict(advice),
            "budget": asdict(self.get_budget_status(additional_cost=advice.estimated_cost_usd or 0.0)),
        }

        existing: list[dict[str, Any]] = []
        if self.history_file.exists():
            try:
                existing = json.loads(self.history_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, ValueError):
                logger.warning("Historique corrompu, réinitialisation")

        existing.append(entry)
        self.history_file.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")


    def get_budget_status(self, additional_cost: float = 0.0) -> BudgetStatus:
        total = additional_cost
        if self.history_file.exists():
            try:
                history = json.loads(self.history_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, ValueError):
                history = []
            for entry in history if isinstance(history, list) else []:
                if entry.get("reason") != "cache_hit":
                    advice = entry.get("advice", {}) if isinstance(entry, dict) else {}
                    total += float(advice.get("estimated_cost_usd", 0) or 0)
        return BudgetStatus(round(total, 6), self.cost_limit_usd, total >= self.cost_limit_usd * 0.8)

    def update_runtime_settings(self, analysis_interval_turns: int | None = None, cost_limit_usd: float | None = None) -> None:
        if analysis_interval_turns is not None:
            self.analysis_interval_turns = max(1, int(analysis_interval_turns))
        if cost_limit_usd is not None:
            self.cost_limit_usd = max(0.01, float(cost_limit_usd))

    def _archive_history_if_new_game(self, turn_number: int) -> None:
        if turn_number != 1 or not self.history_file.exists():
            return
        try:
            history = json.loads(self.history_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, ValueError):
            return
        if not isinstance(history, list) or not history:
            return
        last_turn = int(history[-1].get("turn_number", 0) or 0) if isinstance(history[-1], dict) else 0
        if last_turn <= 1:
            return
        archive_name = f"{self.history_file.stem}.{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
        archive_file = self.history_file.with_name(archive_name)
        archive_file.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")
        self.history_file.write_text("[]", encoding="utf-8")
        logger.info("Nouvelle partie détectée: historique précédent archivé dans %s", archive_file)

    def _find_cached_advice(self, cache_key: str) -> LLMAdvice | None:
        if not self.history_file.exists():
            return None
        try:
            history = json.loads(self.history_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, ValueError):
            return None
        if not isinstance(history, list):
            return None
        for entry in reversed(history):
            if entry.get("cache_key") == cache_key and entry.get("reason") != "cache_hit":
                payload = entry.get("advice", {})
                if isinstance(payload, dict):
                    cached_payload = {**payload, "source": "cache", "estimated_cost_usd": 0.0}
                    return LLMAdvice(**cached_payload)
        return None

    def _cache_key(self, game_state: dict[str, Any]) -> str:
        resources = game_state.get("resources") if isinstance(game_state.get("resources"), dict) else {}
        relevant = {
            "victory_focus": self._build_victory_context(),
            "resource_buckets": _resource_buckets(resources),
            "city_count": _collection_count(game_state.get("cities")),
            "unit_count": _collection_count(game_state.get("units")),
            "game_parameters": game_state.get("game_parameters") or game_state.get("game") or game_state.get("settings") or {},
        }
        blob = json.dumps(relevant, sort_keys=True, ensure_ascii=False, default=str)
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()

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
        game_parameters = game_state.get("game_parameters") or game_state.get("game") or game_state.get("settings")
        reasons: list[str] = []
        if not isinstance(player, dict) or not player:
            reasons.append("identité du joueur absente")
        if cities is not None and isinstance(cities, list) and len(cities) == 0:
            reasons.append("aucune ville détectée")
        if cities is None or units is None:
            reasons.append("données villes/unités non exportées")
        if isinstance(cities, list) and len(cities) == 0 and int(game_state.get("turn_number", 1)) > 1:
            reasons.append("aucune ville détectée après le début de partie")
        if not isinstance(game_parameters, dict):
            reasons.append("paramètres de partie non exportés")
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
            categories={"construction": [], "economie": [], "science": [], "militaire": [], "diplomatie": [], "culture": []},
            action_justifications={
                "Fonder ou sélectionner la capitale si ce n'est pas encore fait.": "Sans ville détectée, le coach ne peut pas prioriser production, science ou économie.",
                "Attendre le prochain export de tour pour inclure villes, unités et paramètres de partie.": "Les paramètres exportés conditionnent les recommandations utiles.",
                "Vérifier que le mod MyTalleyrand exporte bien les sections détaillées du gamestate.": "Un export incomplet provoquerait des conseils trop génériques.",
            },
            source="context_insufficient",
        )


def _resource_buckets(resources: dict[str, Any]) -> dict[str, int]:
    buckets = {"gold": 50, "science": 10, "happiness": 5, "culture": 10}
    result: dict[str, int] = {}
    for key, step in buckets.items():
        try:
            value = float(resources.get(key, 0) or 0)
        except (TypeError, ValueError):
            value = 0
        result[key] = int(value // step)
    return result


def _collection_count(value: Any) -> int:
    return len(value) if isinstance(value, list) else 0
