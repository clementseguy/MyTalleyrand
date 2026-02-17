"""Client LLM avec fallback local pour générer des conseils structurés."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


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
    """Client simplifié.

    La version MVP utilise un fallback local déterministe pour garantir
    un comportement stable même sans accès API.
    """

    def __init__(self, provider: str, model: str):
        self.provider = provider
        self.model = model

    def generate_advice(self, game_state: dict[str, Any], victory_focus: str) -> LLMAdvice:
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
