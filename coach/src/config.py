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

_DEFAULT_SYSTEM_PROMPT = (
    "Tu es Talleyrand, coach stratégique pour Civilization V. "
    "Réponds de manière actionnable et concise en français. "
    "Tu dois impérativement retourner un JSON valide avec les clés: "
    "objective_10_turns, priority_actions, risks, confidence, categories."
)

logger = logging.getLogger(__name__)


_DEFAULT_USER_PROMPT_TEMPLATE = (
    "Objectif de victoire: {victory_focus}\n"
    "Etat de jeu (JSON): {game_state_json}\n"
    "Donne un objectif 10 tours, 3-5 actions prioritaires, risques, confiance (0-100), "
    "et actions catégorisées (economie/science/militaire/diplomatie)."
)


@dataclass(frozen=True)
class AppConfig:
    """Configuration résolue de l'application."""

    schema_version: str
    civ5_dir: Path
    export_dir: Path
    gamestate_file: Path
    log_file: Path
    llm_provider: str
    llm_model: str
    llm_max_tokens: int
    llm_temperature: float
    llm_timeout_seconds: int
    llm_system_prompt: str
    llm_user_prompt_template: str
    llm_api_key: str | None
    overlay_width: int
    overlay_height: int
    overlay_opacity: float


def _expand(path_value: str) -> Path:
    return Path(path_value).expanduser().resolve()


def _env_or_default(env_name: str, default: Any, caster):
    raw = os.getenv(env_name)
    if raw is None or raw == "":
        return default
    return caster(raw)


def _load_json_if_exists(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


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
    settings = _load_json_if_exists(resolved_settings_path)

    configured_user_path = user_settings_path or Path(
        os.getenv("TALLEYRAND_USER_CONFIG", DEFAULT_USER_SETTINGS_PATH)
    ).expanduser()
    user_settings = _load_json_if_exists(configured_user_path)

    paths = settings["paths"]
    llm = settings["llm"]
    llm_user = user_settings.get("llm", {})
    overlay = settings["overlay"]

    system_prompt = _env_or_default(
        "TALLEYRAND_LLM_SYSTEM_PROMPT",
        llm_user.get("system_prompt", _DEFAULT_SYSTEM_PROMPT),
        str,
    )
    user_prompt_template = _env_or_default(
        "TALLEYRAND_LLM_USER_PROMPT_TEMPLATE",
        llm_user.get("user_prompt_template", _DEFAULT_USER_PROMPT_TEMPLATE),
        str,
    )

    llm_provider = _env_or_default("TALLEYRAND_LLM_PROVIDER", llm["provider"], str)
    llm_api_key = _resolve_api_key(llm_provider=llm_provider, llm_user=llm_user)

    config = AppConfig(
        schema_version=settings["schema_version"],
        civ5_dir=_expand(_env_or_default("TALLEYRAND_CIV5_DIR", paths["civ5_user_dir"], str)),
        export_dir=_expand(_env_or_default("TALLEYRAND_EXPORT_DIR", paths["mod_export_dir"], str)),
        gamestate_file=_expand(_env_or_default("TALLEYRAND_GAMESTATE_FILE", paths["gamestate_file"], str)),
        log_file=_expand(_env_or_default("TALLEYRAND_LOG_FILE", paths["log_file"], str)),
        llm_provider=llm_provider,
        llm_model=_env_or_default("TALLEYRAND_LLM_MODEL", llm["model"], str),
        llm_max_tokens=_env_or_default("TALLEYRAND_LLM_MAX_TOKENS", llm["max_tokens"], int),
        llm_temperature=_env_or_default("TALLEYRAND_LLM_TEMPERATURE", llm["temperature"], float),
        llm_timeout_seconds=_env_or_default("TALLEYRAND_LLM_TIMEOUT_SECONDS", llm["timeout_seconds"], int),
        llm_system_prompt=system_prompt,
        llm_user_prompt_template=user_prompt_template,
        llm_api_key=llm_api_key,
        overlay_width=_env_or_default("TALLEYRAND_OVERLAY_WIDTH", overlay["width"], int),
        overlay_height=_env_or_default("TALLEYRAND_OVERLAY_HEIGHT", overlay["height"], int),
        overlay_opacity=_env_or_default("TALLEYRAND_OVERLAY_OPACITY", overlay["opacity"], float),
    )
    return config


def validate_config(config: AppConfig) -> list[str]:
    """Retourne la liste des erreurs de configuration."""
    errors: list[str] = []

    if config.overlay_width <= 0 or config.overlay_height <= 0:
        errors.append("Overlay dimensions must be positive")
    if not (0 < config.overlay_opacity <= 1):
        errors.append("Overlay opacity must be in (0, 1]")
    if config.llm_max_tokens <= 0:
        errors.append("LLM max_tokens must be positive")
    if config.llm_timeout_seconds <= 0:
        errors.append("LLM timeout_seconds must be positive")
    if not (0 <= config.llm_temperature <= 2):
        errors.append("LLM temperature must be between 0 and 2")
    if "{victory_focus}" not in config.llm_user_prompt_template:
        errors.append("LLM user prompt template must include {victory_focus}")
    if "{game_state_json}" not in config.llm_user_prompt_template:
        errors.append("LLM user prompt template must include {game_state_json}")

    return errors
