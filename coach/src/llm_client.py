"""Client LLM (phase 2) avec parsing strict et fallback local robuste."""

from __future__ import annotations

import json
import logging
import os
from dataclasses import asdict, dataclass
from typing import Any

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

_ALLOWED_CATEGORIES = {"economie", "science", "militaire", "diplomatie"}


@dataclass(frozen=True)
class LLMAdvice:
    """Réponse normalisée utilisée par l'overlay et l'historique."""

    objective_10_turns: str
    priority_actions: list[str]
    risks: list[str]
    confidence: int
    categories: dict[str, list[str]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class LLMClient:
    """Client LLM avec retry + timeout logique et fallback local déterministe."""

    def __init__(
        self,
        provider: str,
        model: str,
        timeout_seconds: int = 15,
        max_tokens: int = 500,
        temperature: float = 0.2,
    ):
        self.provider = provider
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.max_tokens = max_tokens
        self.temperature = temperature

    def generate_advice(self, game_state: dict[str, Any], victory_focus: str) -> LLMAdvice:
        try:
            raw = self._generate_remote_advice_raw(game_state=game_state, victory_focus=victory_focus)
            return self._parse_remote_payload(raw)
        except Exception as exc:
            logger.warning("⚠️ LLM distant indisponible (%s), fallback local activé", exc)
            return self._generate_fallback_advice(game_state=game_state, victory_focus=victory_focus)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
        retry=retry_if_exception_type((RuntimeError, ValueError, TimeoutError)),
        reraise=True,
    )
    def _generate_remote_advice_raw(self, game_state: dict[str, Any], victory_focus: str) -> dict[str, Any]:
        if self.provider != "openai":
            raise RuntimeError(f"provider non supporté: {self.provider}")

        api_key = os.getenv("TALLEYRAND_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("clé API OpenAI absente")

        try:
            from openai import OpenAI
        except Exception as exc:  # pragma: no cover - dépendance runtime
            raise RuntimeError("package openai indisponible") from exc

        client = OpenAI(api_key=api_key, timeout=self.timeout_seconds)

        prompt = self._build_prompt(game_state=game_state, victory_focus=victory_focus)
        response = client.responses.create(
            model=self.model,
            temperature=self.temperature,
            max_output_tokens=self.max_tokens,
            input=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Tu es Talleyrand, coach stratégique pour Civ5. "
                                "Réponds UNIQUEMENT en JSON valide avec les clés: "
                                "objective_10_turns, priority_actions, risks, confidence, categories."
                            ),
                        }
                    ],
                },
                {"role": "user", "content": [{"type": "text", "text": prompt}]},
            ],
        )

        content = getattr(response, "output_text", "")
        if not content:
            raise ValueError("réponse vide du provider")

        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError(f"JSON LLM invalide: {exc}") from exc

    @staticmethod
    def _build_prompt(game_state: dict[str, Any], victory_focus: str) -> str:
        return (
            f"Objectif de victoire: {victory_focus}\n"
            f"Etat de jeu (JSON): {json.dumps(game_state, ensure_ascii=False)}\n"
            "Donne un objectif 10 tours, 3-5 actions prioritaires, risques, confiance (0-100), "
            "et actions catégorisées (economie/science/militaire/diplomatie)."
        )

    def _parse_remote_payload(self, payload: dict[str, Any]) -> LLMAdvice:
        required = ["objective_10_turns", "priority_actions", "risks", "confidence", "categories"]
        missing = [key for key in required if key not in payload]
        if missing:
            raise ValueError(f"clés manquantes dans la réponse LLM: {', '.join(missing)}")

        objective = str(payload["objective_10_turns"]).strip()
        actions = payload["priority_actions"]
        risks = payload["risks"]
        confidence = int(payload["confidence"])
        categories = payload["categories"]

        if not objective:
            raise ValueError("objective_10_turns vide")
        if not isinstance(actions, list) or not (3 <= len(actions) <= 5):
            raise ValueError("priority_actions doit contenir entre 3 et 5 éléments")
        if not isinstance(risks, list):
            raise ValueError("risks doit être une liste")
        if not isinstance(categories, dict):
            raise ValueError("categories doit être un objet")
        if not (0 <= confidence <= 100):
            raise ValueError("confidence doit être entre 0 et 100")

        normalized_categories: dict[str, list[str]] = {}
        for category in _ALLOWED_CATEGORIES:
            raw_items = categories.get(category, [])
            if not isinstance(raw_items, list):
                raise ValueError(f"categories.{category} doit être une liste")
            normalized_categories[category] = [str(item).strip() for item in raw_items if str(item).strip()]

        normalized_actions = [str(item).strip() for item in actions if str(item).strip()][:5]
        if len(normalized_actions) < 3:
            raise ValueError("priority_actions normalisé contient moins de 3 actions")

        return LLMAdvice(
            objective_10_turns=objective,
            priority_actions=normalized_actions,
            risks=[str(item).strip() for item in risks if str(item).strip()],
            confidence=confidence,
            categories=normalized_categories,
        )

    def _generate_fallback_advice(self, game_state: dict[str, Any], victory_focus: str) -> LLMAdvice:
        turn_number = int(game_state.get("turn_number", 1))
        resources = game_state.get("resources", {})
        gold = int(resources.get("gold", 0))
        science = int(resources.get("science", 0))

        objective = (
            f"Consolider une stratégie {victory_focus} et préparer le cap du tour {turn_number + 10}."
        )

        actions = [
            "Affecter un citoyen supplémentaire sur une case à forte production.",
            "Maintenir une réserve d'or pour acheter un bâtiment clé.",
            "Prioriser une technologie synergique avec votre objectif de victoire.",
        ]
        if science < 20:
            actions.append("Construire ou acheter une Bibliothèque dans la ville principale.")
        if gold < 100:
            actions.append("Sécuriser une route commerciale rentable dès que possible.")

        categories = {
            "economie": ["Optimiser les routes commerciales", "Limiter les dépenses non critiques"],
            "science": ["Accélérer les bâtiments scientifiques", "Sécuriser des accords de recherche"],
            "militaire": ["Maintenir une armée dissuasive", "Renforcer les frontières exposées"],
            "diplomatie": ["Éviter les guerres multiples", "Négocier des échanges favorables"],
        }

        return LLMAdvice(
            objective_10_turns=objective,
            priority_actions=actions[:5],
            risks=["Retard scientifique", "Économie insuffisante pour soutenir l'expansion"],
            confidence=78,
            categories=categories,
        )
