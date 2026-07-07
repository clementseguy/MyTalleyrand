"""Client LLM (phase 2) avec parsing strict et fallback local robuste."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from typing import Any, Callable

from tenacity import RetryCallState, retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from src.config import _DEFAULT_SYSTEM_PROMPT, _DEFAULT_USER_PROMPT_TEMPLATE

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
    source: str = "remote"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LLMStatus:
    """Statut UX court lié à la disponibilité du provider LLM."""

    title: str
    message: str
    suggestion: str


def _notify_retry_status(retry_state: RetryCallState) -> None:
    client = retry_state.args[0] if retry_state.args else None
    if not isinstance(client, LLMClient):
        return

    next_attempt = retry_state.attempt_number + 1
    delay = retry_state.next_action.sleep if retry_state.next_action else 0
    exception = retry_state.outcome.exception() if retry_state.outcome else None
    client._notify_status(
        LLMStatus(
            title="Reconnexion LLM en cours",
            message=(
                f"Le provider LLM ne répond pas ({exception}). "
                f"Nouvelle tentative {next_attempt}/3 dans {delay:.1f}s."
            ),
            suggestion="Gardez la partie ouverte : MyTalleyrand réessaie automatiquement.",
        )
    )


class LLMClient:
    """Client LLM avec retry + timeout logique, statuts UX et fallback local déterministe."""

    def __init__(
        self,
        provider: str,
        model: str,
        timeout_seconds: int = 15,
        max_tokens: int = 500,
        temperature: float = 0.2,
        system_prompt: str = _DEFAULT_SYSTEM_PROMPT,
        user_prompt_template: str = _DEFAULT_USER_PROMPT_TEMPLATE,
        api_key: str | None = None,
        status_callback: Callable[[LLMStatus], None] | None = None,
    ):
        self.provider = provider
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.system_prompt = system_prompt.strip() or _DEFAULT_SYSTEM_PROMPT
        self.user_prompt_template = user_prompt_template
        self.api_key = api_key
        self._openai_client = None
        self.status_callback = status_callback

    def generate_advice(self, game_state: dict[str, Any], victory_focus: str) -> LLMAdvice:
        try:
            raw = self._generate_remote_advice_raw(game_state=game_state, victory_focus=victory_focus)
            return self._parse_remote_payload(raw)
        except Exception as exc:
            logger.warning("⚠️ LLM distant indisponible (%s), fallback local activé", exc)
            self._notify_status(
                LLMStatus(
                    title="Fallback LLM activé",
                    message="Le conseil distant est indisponible après 3 tentatives. Un conseil local est affiché à la place.",
                    suggestion="Vérifiez votre connexion réseau ou votre clé API ; MyTalleyrand réessaiera au prochain tour analysé.",
                )
            )
            return self._generate_fallback_advice(game_state=game_state, victory_focus=victory_focus)

    def _notify_status(self, status: LLMStatus) -> None:
        if self.status_callback is None:
            return
        try:
            self.status_callback(status)
        except Exception as exc:  # pragma: no cover - défense contre une UI défaillante
            logger.warning("Impossible d'afficher le statut LLM (%s)", exc)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
        retry=retry_if_exception_type((RuntimeError, ValueError, TimeoutError)),
        before_sleep=_notify_retry_status,
        reraise=True,
    )
    def _generate_remote_advice_raw(self, game_state: dict[str, Any], victory_focus: str) -> dict[str, Any]:
        if self.provider != "openai":
            raise RuntimeError(f"provider non supporté: {self.provider}")

        if not self.api_key:
            raise RuntimeError("clé API OpenAI absente")

        if self._openai_client is None:
            try:
                from openai import OpenAI
            except Exception as exc:  # pragma: no cover - dépendance runtime
                raise RuntimeError("package openai indisponible") from exc
            self._openai_client = OpenAI(api_key=self.api_key, timeout=self.timeout_seconds)

        client = self._openai_client

        prompt = self._build_prompt(game_state=game_state, victory_focus=victory_focus)
        response = client.responses.create(
            model=self.model,
            temperature=self.temperature,
            max_output_tokens=self.max_tokens,
            input=[
                {
                    "role": "system",
                    "content": [{"type": "text", "text": self.system_prompt}],
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

    def _build_prompt(self, game_state: dict[str, Any], victory_focus: str) -> str:
        return self.user_prompt_template.format(
            victory_focus=victory_focus,
            game_state_json=json.dumps(game_state, ensure_ascii=False),
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
            source="remote",
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
            source="local_fallback",
        )
