"""Client LLM (phase 2) avec parsing strict et fallback local robuste."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from typing import Any, Callable

import httpx
from openai import APIConnectionError, APIError, APITimeoutError, OpenAI, RateLimitError
from tenacity import RetryCallState, retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from src.config import DEFAULT_SYSTEM_PROMPT, DEFAULT_USER_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)

_ALLOWED_CATEGORIES = {"construction", "economie", "science", "militaire", "diplomatie", "culture"}
_SUPPORTED_PROVIDERS = {"mistral", "openai"}
_MISTRAL_CHAT_COMPLETIONS_URL = "https://api.mistral.ai/v1/chat/completions"


@dataclass(frozen=True)
class LLMAdvice:
    """Réponse normalisée utilisée par l'overlay et l'historique."""

    objective_10_turns: str
    priority_actions: list[str]
    risks: list[str]
    confidence: int
    categories: dict[str, list[str]]
    action_justifications: dict[str, str] = field(default_factory=dict)
    source: str = "remote"
    prompt_tokens: int = 0
    completion_tokens: int = 0
    estimated_cost_usd: float | None = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class LLMResponseError(ValueError):
    """Réponse distante reçue mais inutilisable (format/schema)."""


class LLMProviderError(RuntimeError):
    """Erreur provider normalisée pour décider du retry et du message UX."""

    def __init__(self, provider: str, kind: str, message: str, *, retryable: bool = False):
        super().__init__(message)
        self.provider = provider
        self.kind = kind
        self.retryable = retryable


class LLMRetryableProviderError(LLMProviderError):
    """Erreur provider transitoire éligible aux retries."""

    def __init__(self, provider: str, kind: str, message: str):
        super().__init__(provider, kind, message, retryable=True)


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
    provider = getattr(exception, "provider", client.provider)
    client._notify_status(
        LLMStatus(
            title="Reconnexion LLM en cours",
            message=(
                f"Le provider LLM {provider} ne répond pas ({exception}). "
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
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        user_prompt_template: str = DEFAULT_USER_PROMPT_TEMPLATE,
        detail_level: str = "standard",
        api_key: str | None = None,
        status_callback: Callable[[LLMStatus], None] | None = None,
    ):
        self.provider = provider
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.system_prompt = system_prompt.strip() or DEFAULT_SYSTEM_PROMPT
        self.user_prompt_template = user_prompt_template
        self.detail_level = _normalize_detail_level(detail_level)
        self.api_key = api_key
        self._openai_client = None
        self._mistral_http_client: httpx.Client | None = None
        self.status_callback = status_callback

    @property
    def effective_max_output_tokens(self) -> int:
        return detail_level_max_tokens(self.max_tokens, self.detail_level)

    def generate_advice(self, game_state: dict[str, Any], victory_focus: str) -> LLMAdvice:
        try:
            raw = self._generate_remote_advice_raw(game_state=game_state, victory_focus=victory_focus)
            return self._parse_remote_payload(raw)
        except LLMResponseError as exc:
            logger.warning("⚠️ Réponse LLM invalide (%s), fallback local activé", exc)
            self._notify_status(
                LLMStatus(
                    title="Réponse LLM invalide",
                    message="Le provider a répondu, mais le format ne respecte pas le schéma attendu. Un conseil local est affiché.",
                    suggestion="Réessayez au prochain tour analysé ; si le problème persiste, vérifiez les prompts personnalisés.",
                )
            )
            return self._generate_fallback_advice(game_state=game_state, victory_focus=victory_focus)
        except LLMProviderError as exc:
            logger.warning("⚠️ LLM %s indisponible (%s), fallback local activé", exc.provider, exc)
            self._notify_status(status_for_provider_error(exc))
            return self._generate_fallback_advice(game_state=game_state, victory_focus=victory_focus)
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
        retry=retry_if_exception_type(LLMRetryableProviderError),
        before_sleep=_notify_retry_status,
        reraise=True,
    )
    def _generate_remote_advice_raw(self, game_state: dict[str, Any], victory_focus: str) -> dict[str, Any]:
        provider = self.provider.strip().lower()
        if provider not in _SUPPORTED_PROVIDERS:
            raise LLMProviderError(provider, "config", f"provider non supporté: {self.provider}")

        if not self.api_key:
            raise LLMProviderError(provider, "auth", f"clé API {provider} absente")

        if provider == "mistral":
            return self._generate_mistral_advice_raw(game_state=game_state, victory_focus=victory_focus)

        return self._generate_openai_advice_raw(game_state=game_state, victory_focus=victory_focus)

    def _generate_openai_advice_raw(self, game_state: dict[str, Any], victory_focus: str) -> dict[str, Any]:
        if self._openai_client is None:
            self._openai_client = OpenAI(api_key=self.api_key, timeout=self.timeout_seconds)

        client = self._openai_client

        prompt = self._build_prompt(game_state=game_state, victory_focus=victory_focus)
        try:
            response = client.responses.create(
                model=self.model,
                temperature=self.temperature,
                max_output_tokens=self.effective_max_output_tokens,
                input=[
                    {
                        "role": "system",
                        "content": [{"type": "text", "text": self.system_prompt}],
                    },
                    {"role": "user", "content": [{"type": "text", "text": prompt}]},
                ],
            )
        except (APITimeoutError, APIConnectionError) as exc:
            raise LLMRetryableProviderError("openai", "network", str(exc)) from exc
        except RateLimitError as exc:
            raise _map_openai_api_error(exc) from exc
        except APIError as exc:
            raise _map_openai_api_error(exc) from exc

        content = getattr(response, "output_text", "")
        if not content:
            raise LLMResponseError("réponse vide du provider")

        try:
            payload = json.loads(content)
            if isinstance(payload, dict):
                usage = getattr(response, "usage", None)
                input_tokens = int(getattr(usage, "input_tokens", 0) or 0) if usage is not None else 0
                output_tokens = int(getattr(usage, "output_tokens", 0) or 0) if usage is not None else 0
                payload["_usage"] = {"prompt_tokens": input_tokens, "completion_tokens": output_tokens}
            return payload
        except json.JSONDecodeError as exc:
            raise LLMResponseError(f"JSON LLM invalide: {exc}") from exc

    def _generate_mistral_advice_raw(self, game_state: dict[str, Any], victory_focus: str) -> dict[str, Any]:
        if self._mistral_http_client is None:
            self._mistral_http_client = httpx.Client(timeout=self.timeout_seconds)

        prompt = self._build_prompt(game_state=game_state, victory_focus=victory_focus)
        try:
            response = self._mistral_http_client.post(
                _MISTRAL_CHAT_COMPLETIONS_URL,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={
                    "model": self.model,
                    "temperature": self.temperature,
                    "max_tokens": self.effective_max_output_tokens,
                    "response_format": {"type": "json_object"},
                    "messages": [
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                },
            )
        except (httpx.TimeoutException, httpx.NetworkError) as exc:
            raise LLMRetryableProviderError("mistral", "network", str(exc)) from exc
        except httpx.HTTPError as exc:
            raise LLMRetryableProviderError("mistral", "network", str(exc)) from exc

        if response.status_code >= 400:
            raise _map_mistral_http_error(response)

        try:
            body = response.json()
        except json.JSONDecodeError as exc:
            raise LLMResponseError(f"JSON Mistral invalide: {exc}") from exc

        choices = body.get("choices") if isinstance(body, dict) else None
        if not isinstance(choices, list) or not choices:
            raise LLMResponseError("réponse Mistral sans choix")
        message = choices[0].get("message") if isinstance(choices[0], dict) else None
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, str) or not content.strip():
            raise LLMResponseError("réponse vide du provider")

        try:
            payload = json.loads(content)
        except json.JSONDecodeError as exc:
            raise LLMResponseError(f"JSON LLM invalide: {exc}") from exc

        if isinstance(payload, dict):
            usage = body.get("usage") if isinstance(body.get("usage"), dict) else {}
            payload["_usage"] = {
                "prompt_tokens": int(usage.get("prompt_tokens", 0) or 0),
                "completion_tokens": int(usage.get("completion_tokens", 0) or 0),
            }
        return payload

    def _build_prompt(self, game_state: dict[str, Any], victory_focus: str) -> str:
        detail_instruction = _detail_instruction(self.detail_level)
        return self.user_prompt_template.format(
            victory_focus=victory_focus,
            game_state_json=json.dumps(_sanitize_game_state_for_prompt(game_state), ensure_ascii=False),
        ) + f"\nNiveau de détail attendu: {detail_instruction}"

    def _parse_remote_payload(self, payload: dict[str, Any]) -> LLMAdvice:
        required = ["objective_10_turns", "priority_actions", "risks", "confidence", "categories"]
        missing = [key for key in required if key not in payload]
        if missing:
            raise LLMResponseError(f"clés manquantes dans la réponse LLM: {', '.join(missing)}")

        objective = str(payload["objective_10_turns"]).strip()
        actions = payload["priority_actions"]
        risks = payload["risks"]
        try:
            confidence = int(payload["confidence"])
        except (TypeError, ValueError) as exc:
            raise LLMResponseError("confidence doit être un entier") from exc
        categories = payload["categories"]

        if not objective:
            raise LLMResponseError("objective_10_turns vide")
        if not isinstance(actions, list) or not (3 <= len(actions) <= 5):
            raise LLMResponseError("priority_actions doit contenir entre 3 et 5 éléments")
        if not isinstance(risks, list):
            raise LLMResponseError("risks doit être une liste")
        if not isinstance(categories, dict):
            raise LLMResponseError("categories doit être un objet")
        if not (0 <= confidence <= 100):
            raise LLMResponseError("confidence doit être entre 0 et 100")

        normalized_categories: dict[str, list[str]] = {}
        for category in _ALLOWED_CATEGORIES:
            raw_items = categories.get(category, [])
            if not isinstance(raw_items, list):
                raise LLMResponseError(f"categories.{category} doit être une liste")
            normalized_categories[category] = [str(item).strip() for item in raw_items if str(item).strip()]

        normalized_actions = [str(item).strip() for item in actions if str(item).strip()][:5]
        if len(normalized_actions) < 3:
            raise LLMResponseError("priority_actions normalisé contient moins de 3 actions")

        raw_justifications = payload.get("action_justifications", {})
        action_justifications = _normalize_action_justifications(raw_justifications, normalized_actions)

        usage = payload.get("_usage") if isinstance(payload.get("_usage"), dict) else {}
        prompt_tokens = int(usage.get("prompt_tokens", 0) or 0)
        completion_tokens = int(usage.get("completion_tokens", 0) or 0)
        return LLMAdvice(
            objective_10_turns=objective,
            priority_actions=normalized_actions,
            risks=[str(item).strip() for item in risks if str(item).strip()],
            confidence=confidence,
            categories=normalized_categories,
            action_justifications=action_justifications,
            source="remote",
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            estimated_cost_usd=estimate_cost_usd(self.provider, self.model, prompt_tokens, completion_tokens),
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
            "construction": ["Prioriser un bâtiment utile dans la capitale"],
            "economie": ["Optimiser les routes commerciales", "Limiter les dépenses non critiques"],
            "science": ["Accélérer les bâtiments scientifiques", "Sécuriser des accords de recherche"],
            "militaire": ["Maintenir une armée dissuasive", "Renforcer les frontières exposées"],
            "diplomatie": ["Éviter les guerres multiples", "Négocier des échanges favorables"],
            "culture": ["Stabiliser le bonheur et les politiques sociales"],
        }

        return LLMAdvice(
            objective_10_turns=objective,
            priority_actions=actions[:5],
            risks=["Retard scientifique", "Économie insuffisante pour soutenir l'expansion"],
            confidence=78,
            categories=categories,
            action_justifications={action: "Justification locale basée sur les ressources et le focus de victoire." for action in actions[:5]},
            source="local_fallback",
        )


def _normalize_action_justifications(raw: Any, actions: list[str]) -> dict[str, str]:
    if not isinstance(raw, dict):
        return {}
    normalized: dict[str, str] = {}
    for action in actions:
        value = raw.get(action)
        if value is not None and str(value).strip():
            normalized[action] = str(value).strip()[:240]
    return normalized


def _sanitize_game_state_for_prompt(game_state: dict[str, Any]) -> dict[str, Any]:
    resources = game_state.get("resources") if isinstance(game_state.get("resources"), dict) else {}
    params = game_state.get("game_parameters") or game_state.get("game") or game_state.get("settings")
    sanitized: dict[str, Any] = {
        "schema_version": str(game_state.get("schema_version", ""))[:16],
        "turn_id": int(game_state.get("turn_id", 0)),
        "turn_number": int(game_state.get("turn_number", 0)),
        "resources": {
            "gold": int(resources.get("gold", 0)),
            "science": int(resources.get("science", 0)),
        },
        "game_parameters": _sanitize_mapping(params, {"difficulty", "map_size", "game_speed"}),
        "cities": _sanitize_collection(game_state.get("cities"), {"id", "name", "population", "production"}),
        "units": _sanitize_collection(game_state.get("units"), {"id", "type", "x", "y", "moves"}),
    }
    player = game_state.get("player") if isinstance(game_state.get("player"), dict) else {}
    sanitized["player"] = _sanitize_mapping(player, {"id", "civilization", "leader"})
    return sanitized


def _sanitize_mapping(value: Any, allowed: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    return {str(key): _sanitize_scalar(raw) for key, raw in value.items() if str(key) in allowed}


def _sanitize_collection(value: Any, allowed: set[str], limit: int = 20) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [_sanitize_mapping(item, allowed) for item in value[:limit] if isinstance(item, dict)]


def _sanitize_scalar(value: Any) -> Any:
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, (int, float)):
        return value
    return str(value).replace("\n", " ").replace("\r", " ")[:120]


def _normalize_detail_level(value: str) -> str:
    normalized = str(value).strip().lower()
    return normalized if normalized in {"brief", "standard", "detailed"} else "standard"


def _detail_instruction(detail_level: str) -> str:
    if detail_level == "brief":
        return "réponse très concise, justifications d’une phrase maximum."
    if detail_level == "detailed":
        return "réponse plus détaillée, avec contexte et arbitrages, sans dépasser 5 actions."
    return "réponse équilibrée et directement actionnable."


def detail_level_max_tokens(configured_max_tokens: int, detail_level: str) -> int:
    if detail_level == "brief":
        return min(configured_max_tokens, 250)
    if detail_level == "detailed":
        return max(configured_max_tokens, 700)
    return configured_max_tokens


# Tarifs indicatifs USD / 1M tokens pour estimation UX, pas facturation.
_OPENAI_PRICING_USD_PER_MILLION = {
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4.1-mini": (0.40, 1.60),
    "gpt-4.1-nano": (0.10, 0.40),
}

_MISTRAL_PRICING_USD_PER_MILLION = {
    "mistral-small-latest": (0.15, 0.60),
    "mistral-large-latest": (0.50, 1.50),
    "mistral-medium-latest": (1.50, 7.50),
}


def status_for_provider_error(error: LLMProviderError) -> LLMStatus:
    provider = _provider_display_name(error.provider)
    if error.kind == "auth":
        return LLMStatus(
            title=f"Clé API {provider} invalide",
            message=f"MyTalleyrand ne peut pas authentifier le provider {error.provider}. Un conseil local est affiché.",
            suggestion=f"Vérifiez la clé dans le Keychain avec `python3 -m src.keychain set {error.provider}`.",
        )
    if error.kind == "quota":
        return LLMStatus(
            title=f"Crédit {provider} épuisé",
            message=f"Le provider {error.provider} refuse l'appel pour quota, crédit ou facturation. Un conseil local est affiché.",
            suggestion="Ajoutez du crédit côté provider ou passez temporairement sur l'autre provider dans la configuration.",
        )
    if error.kind == "network":
        return LLMStatus(
            title=f"Réseau {provider} indisponible",
            message=f"Le provider {error.provider} ne répond pas après les tentatives prévues. Un conseil local est affiché.",
            suggestion="Vérifiez la connexion réseau ; MyTalleyrand réessaiera au prochain tour analysé.",
        )
    return LLMStatus(
        title=f"Fallback {provider} activé",
        message=f"Le provider {error.provider} est indisponible ({error}). Un conseil local est affiché.",
        suggestion="Vérifiez la configuration LLM ou utilisez le provider de secours.",
    )


def estimate_openai_cost_usd(model: str, prompt_tokens: int, completion_tokens: int) -> float | None:
    pricing = _OPENAI_PRICING_USD_PER_MILLION.get(model)
    if pricing is None:
        return None
    input_price, output_price = pricing
    return round((prompt_tokens / 1_000_000 * input_price) + (completion_tokens / 1_000_000 * output_price), 6)


def estimate_mistral_cost_usd(model: str, prompt_tokens: int, completion_tokens: int) -> float | None:
    pricing = _MISTRAL_PRICING_USD_PER_MILLION.get(model)
    if pricing is None:
        return None
    input_price, output_price = pricing
    return round((prompt_tokens / 1_000_000 * input_price) + (completion_tokens / 1_000_000 * output_price), 6)


def estimate_cost_usd(provider: str, model: str, prompt_tokens: int, completion_tokens: int) -> float | None:
    normalized_provider = provider.strip().lower()
    if normalized_provider == "openai":
        return estimate_openai_cost_usd(model, prompt_tokens, completion_tokens)
    if normalized_provider == "mistral":
        return estimate_mistral_cost_usd(model, prompt_tokens, completion_tokens)
    return None


def estimate_game_budget_usd(model: str, prompt_tokens: int, completion_tokens: int, analyses: int) -> float | None:
    single_call = estimate_openai_cost_usd(model, prompt_tokens, completion_tokens)
    if single_call is None:
        return None
    return round(single_call * max(0, analyses), 6)


def _map_openai_api_error(exc: APIError) -> LLMProviderError:
    status_code = int(getattr(exc, "status_code", 0) or 0)
    body = getattr(exc, "body", None)
    text = _error_payload_text(body) or str(exc)
    if status_code in {401, 403}:
        return LLMProviderError("openai", "auth", text)
    if _looks_like_quota_error(text):
        return LLMProviderError("openai", "quota", text)
    if status_code == 429:
        return LLMRetryableProviderError("openai", "network", text)
    if status_code >= 500 or status_code == 0:
        return LLMRetryableProviderError("openai", "network", text)
    return LLMProviderError("openai", "provider", text)


def _map_mistral_http_error(response: httpx.Response) -> LLMProviderError:
    text = _response_error_text(response)
    if response.status_code in {401, 403}:
        return LLMProviderError("mistral", "auth", text)
    if response.status_code == 402 or _looks_like_quota_error(text):
        return LLMProviderError("mistral", "quota", text)
    if response.status_code == 429:
        return LLMRetryableProviderError("mistral", "network", text)
    if response.status_code >= 500:
        return LLMRetryableProviderError("mistral", "network", text)
    return LLMProviderError("mistral", "provider", text)


def _response_error_text(response: httpx.Response) -> str:
    try:
        return _error_payload_text(response.json())
    except json.JSONDecodeError:
        return response.text[:500]


def _error_payload_text(payload: Any) -> str:
    if isinstance(payload, dict):
        error = payload.get("error")
        if isinstance(error, dict):
            parts = [str(error.get(key, "")) for key in ("code", "type", "message") if error.get(key)]
            return " ".join(parts)
        if error:
            return str(error)
        parts = [str(payload.get(key, "")) for key in ("code", "type", "message", "detail") if payload.get(key)]
        return " ".join(parts)
    return str(payload) if payload else ""


def _looks_like_quota_error(text: str) -> bool:
    normalized = text.lower()
    markers = ("insufficient_quota", "quota", "credit", "credits", "billing", "payment")
    return any(marker in normalized for marker in markers)


def _provider_display_name(provider: str) -> str:
    normalized = provider.strip().lower()
    if normalized == "openai":
        return "OpenAI"
    if normalized == "mistral":
        return "Mistral"
    return provider.capitalize()
