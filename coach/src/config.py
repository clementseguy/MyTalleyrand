"""Gestion de la configuration du coach (settings + variables d'environnement)."""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.keychain import get_api_key

DEFAULT_SETTINGS_PATH = Path(__file__).resolve().parents[1] / "config" / "settings.json"
DEFAULT_USER_SETTINGS_PATH = Path.home() / "Library" / "Application Support" / "MyTalleyrand" / "coach.user.json"

# Sources de gamestate supportées.
GAMESTATE_SOURCES = ("sqlite", "file")
# Base SQLite ModUserData écrite par le mod sur macOS (émulation Aspyr sans io/os).
DEFAULT_GAMESTATE_DB = (
    "~/Library/Application Support/Sid Meier's Civilization 5/"
    "ModUserData/a1b2c3d4-e5f6-7890-abcd-ef1234567890-1.db"
)

DEFAULT_SYSTEM_PROMPT = (
    "Tu es Talleyrand, coach stratégique pour Civilization V. "
    "Réponds de manière actionnable et concise en français. "
    "Tu dois impérativement retourner un JSON valide avec les clés: "
    "objective_10_turns, priority_actions, action_justifications, risks, confidence, categories."
)

logger = logging.getLogger(__name__)


class ConfigError(ValueError):
    """Configuration application absente, corrompue ou incomplète."""


DEFAULT_USER_PROMPT_TEMPLATE = (
    "Objectif de victoire: {victory_focus}\n"
    "Etat de jeu (JSON): {game_state_json}\n"
    "Donne un objectif 10 tours, 3-5 actions prioritaires, risques, confiance (0-100), "
    "actions catégorisées (construction/economie/science/militaire/diplomatie/culture), et justification courte par action."
)


@dataclass(frozen=True)
class AppConfig:
    """Configuration résolue de l'application."""

    schema_version: str
    civ5_dir: Path
    export_dir: Path
    gamestate_source: str
    gamestate_db: Path
    gamestate_file: Path
    log_file: Path
    llm_provider: str
    llm_model: str
    llm_max_tokens: int
    llm_temperature: float
    llm_timeout_seconds: int
    llm_detail_level: str
    cost_limit_usd: float
    llm_system_prompt: str
    llm_user_prompt_template: str
    llm_api_key: str | None
    overlay_width: int
    overlay_height: int
    overlay_opacity: float
    analysis_interval_turns: int


def _expand(path_value: str) -> Path:
    return Path(path_value).expanduser().resolve()


def _env_or_default(env_name: str, default: Any, caster):
    raw = os.getenv(env_name)
    value = default if raw is None or raw == "" else raw
    try:
        return caster(value)
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"Configuration invalide: {env_name}={value!r} n’est pas compatible avec {caster.__name__}") from exc


def _load_json_if_exists(path: Path, *, required: bool = False) -> dict[str, Any]:
    if not path.exists():
        if required:
            raise ConfigError(f"Fichier de configuration introuvable: {path}")
        return {}
    try:
        with path.open("r", encoding="utf-8") as file:
            payload = json.load(file)
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Fichier de configuration JSON invalide: {path} ({exc})") from exc
    if not isinstance(payload, dict):
        raise ConfigError(f"Fichier de configuration invalide: {path} doit contenir un objet JSON")
    return payload


def _require_mapping(payload: dict[str, Any], key: str, source: Path) -> dict[str, Any]:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise ConfigError(f"Configuration invalide: section '{key}' manquante ou invalide dans {source}")
    return value


def _require_key(payload: dict[str, Any], key: str, section: str, source: Path) -> Any:
    if key not in payload:
        raise ConfigError(f"Configuration invalide: clé '{section}.{key}' manquante dans {source}")
    return payload[key]


def _resolve_api_key(llm_provider: str, llm_user: dict[str, Any]) -> str | None:
    env_key = os.getenv("TALLEYRAND_OPENAI_API_KEY")
    if env_key:
        return env_key

    keychain_key = get_api_key(llm_provider)
    if keychain_key:
        return keychain_key

    legacy_file_key = llm_user.get("api_key")
    if legacy_file_key and legacy_file_key != "<OPENAI_API_KEY>":
        logger.warning(
            "Clé API lue depuis le fichier utilisateur legacy; migrez-la vers le Keychain macOS"
        )
        return str(legacy_file_key)

    return None


def load_config(settings_path: Path | None = None, user_settings_path: Path | None = None) -> AppConfig:
    """Charge la configuration depuis le JSON et applique les surcharges d'environnement."""
    resolved_settings_path = settings_path or DEFAULT_SETTINGS_PATH
    settings = _load_json_if_exists(resolved_settings_path, required=True)

    configured_user_path = user_settings_path or Path(
        os.getenv("TALLEYRAND_USER_CONFIG", DEFAULT_USER_SETTINGS_PATH)
    ).expanduser()
    user_settings = _load_json_if_exists(configured_user_path)

    paths = _require_mapping(settings, "paths", resolved_settings_path)
    llm = _require_mapping(settings, "llm", resolved_settings_path)
    llm_user = user_settings.get("llm", {})
    if not isinstance(llm_user, dict):
        raise ConfigError(f"Configuration utilisateur invalide: section 'llm' invalide dans {configured_user_path}")
    overlay = _require_mapping(settings, "overlay", resolved_settings_path)
    coach = settings.get("coach", {})
    if coach and not isinstance(coach, dict):
        raise ConfigError(f"Configuration invalide: section 'coach' invalide dans {resolved_settings_path}")

    system_prompt = _env_or_default(
        "TALLEYRAND_LLM_SYSTEM_PROMPT",
        llm_user.get("system_prompt", DEFAULT_SYSTEM_PROMPT),
        str,
    )
    user_prompt_template = _env_or_default(
        "TALLEYRAND_LLM_USER_PROMPT_TEMPLATE",
        llm_user.get("user_prompt_template", DEFAULT_USER_PROMPT_TEMPLATE),
        str,
    )

    llm_provider = _env_or_default(
        "TALLEYRAND_LLM_PROVIDER",
        _require_key(llm, "provider", "llm", resolved_settings_path),
        str,
    )
    llm_api_key = _resolve_api_key(llm_provider=llm_provider, llm_user=llm_user)

    config = AppConfig(
        schema_version=_require_key(settings, "schema_version", "root", resolved_settings_path),
        civ5_dir=_expand(
            _env_or_default(
                "TALLEYRAND_CIV5_DIR",
                _require_key(paths, "civ5_user_dir", "paths", resolved_settings_path),
                str,
            )
        ),
        export_dir=_expand(
            _env_or_default(
                "TALLEYRAND_EXPORT_DIR",
                _require_key(paths, "mod_export_dir", "paths", resolved_settings_path),
                str,
            )
        ),
        gamestate_source=_env_or_default(
            "TALLEYRAND_GAMESTATE_SOURCE",
            paths.get("gamestate_source", "sqlite"),
            str,
        ),
        gamestate_db=_expand(
            _env_or_default(
                "TALLEYRAND_GAMESTATE_DB",
                paths.get("gamestate_db", DEFAULT_GAMESTATE_DB),
                str,
            )
        ),
        gamestate_file=_expand(
            _env_or_default(
                "TALLEYRAND_GAMESTATE_FILE",
                _require_key(paths, "gamestate_file", "paths", resolved_settings_path),
                str,
            )
        ),
        log_file=_expand(
            _env_or_default(
                "TALLEYRAND_LOG_FILE",
                _require_key(paths, "log_file", "paths", resolved_settings_path),
                str,
            )
        ),
        llm_provider=llm_provider,
        llm_model=_env_or_default(
            "TALLEYRAND_LLM_MODEL",
            _require_key(llm, "model", "llm", resolved_settings_path),
            str,
        ),
        llm_max_tokens=_env_or_default(
            "TALLEYRAND_LLM_MAX_TOKENS",
            _require_key(llm, "max_tokens", "llm", resolved_settings_path),
            int,
        ),
        llm_temperature=_env_or_default(
            "TALLEYRAND_LLM_TEMPERATURE",
            _require_key(llm, "temperature", "llm", resolved_settings_path),
            float,
        ),
        llm_timeout_seconds=_env_or_default(
            "TALLEYRAND_LLM_TIMEOUT_SECONDS",
            _require_key(llm, "timeout_seconds", "llm", resolved_settings_path),
            int,
        ),
        llm_detail_level=_env_or_default(
            "TALLEYRAND_LLM_DETAIL_LEVEL",
            coach.get("detail_level", "standard"),
            str,
        ),
        cost_limit_usd=_env_or_default(
            "TALLEYRAND_COST_LIMIT_USD",
            coach.get("cost_limit_usd", 2.0),
            float,
        ),
        llm_system_prompt=system_prompt,
        llm_user_prompt_template=user_prompt_template,
        llm_api_key=llm_api_key,
        overlay_width=_env_or_default(
            "TALLEYRAND_OVERLAY_WIDTH",
            _require_key(overlay, "width", "overlay", resolved_settings_path),
            int,
        ),
        overlay_height=_env_or_default(
            "TALLEYRAND_OVERLAY_HEIGHT",
            _require_key(overlay, "height", "overlay", resolved_settings_path),
            int,
        ),
        overlay_opacity=_env_or_default(
            "TALLEYRAND_OVERLAY_OPACITY",
            _require_key(overlay, "opacity", "overlay", resolved_settings_path),
            float,
        ),
        analysis_interval_turns=_env_or_default(
            "TALLEYRAND_ANALYSIS_INTERVAL_TURNS",
            coach.get("analysis_interval_turns", 10),
            int,
        ),
    )
    return config


def validate_config(config: AppConfig) -> list[str]:
    """Retourne la liste des erreurs de configuration."""
    errors: list[str] = []

    if config.overlay_width <= 0 or config.overlay_height <= 0:
        errors.append("Overlay dimensions must be positive")
    if not (0 < config.overlay_opacity <= 1):
        errors.append("Overlay opacity must be in (0, 1]")
    if not isinstance(config.llm_max_tokens, int) or config.llm_max_tokens <= 0:
        errors.append("LLM max_tokens must be a positive integer")
    if not isinstance(config.llm_timeout_seconds, int) or config.llm_timeout_seconds <= 0:
        errors.append("LLM timeout_seconds must be a positive integer")
    if not isinstance(config.llm_temperature, (int, float)) or not (0 <= config.llm_temperature <= 2):
        errors.append("LLM temperature must be a number between 0 and 2")
    if not isinstance(config.analysis_interval_turns, int) or config.analysis_interval_turns <= 0:
        errors.append("Analysis interval must be a positive integer")
    if config.llm_detail_level not in {"brief", "standard", "detailed"}:
        errors.append("LLM detail_level must be brief, standard, or detailed")
    if config.gamestate_source not in GAMESTATE_SOURCES:
        errors.append(f"gamestate_source must be one of {GAMESTATE_SOURCES}")
    if not isinstance(config.cost_limit_usd, (int, float)) or config.cost_limit_usd <= 0:
        errors.append("Cost limit must be a positive number")
    if "{victory_focus}" not in config.llm_user_prompt_template:
        errors.append("LLM user prompt template must include {victory_focus}")
    if "{game_state_json}" not in config.llm_user_prompt_template:
        errors.append("LLM user prompt template must include {game_state_json}")

    return errors
