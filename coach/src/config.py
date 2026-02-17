"""Gestion de la configuration du coach (settings + variables d'environnement)."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_SETTINGS_PATH = Path(__file__).resolve().parents[1] / "config" / "settings.json"


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


def load_config(settings_path: Path | None = None) -> AppConfig:
    """Charge la configuration depuis le JSON et applique les surcharges d'environnement."""
    resolved_settings_path = settings_path or DEFAULT_SETTINGS_PATH
    with resolved_settings_path.open("r", encoding="utf-8") as f:
        settings = json.load(f)

    paths = settings["paths"]
    llm = settings["llm"]
    overlay = settings["overlay"]

    config = AppConfig(
        schema_version=settings["schema_version"],
        civ5_dir=_expand(_env_or_default("TALLEYRAND_CIV5_DIR", paths["civ5_user_dir"], str)),
        export_dir=_expand(_env_or_default("TALLEYRAND_EXPORT_DIR", paths["mod_export_dir"], str)),
        gamestate_file=_expand(_env_or_default("TALLEYRAND_GAMESTATE_FILE", paths["gamestate_file"], str)),
        log_file=_expand(_env_or_default("TALLEYRAND_LOG_FILE", paths["log_file"], str)),
        llm_provider=_env_or_default("TALLEYRAND_LLM_PROVIDER", llm["provider"], str),
        llm_model=_env_or_default("TALLEYRAND_LLM_MODEL", llm["model"], str),
        llm_max_tokens=_env_or_default("TALLEYRAND_LLM_MAX_TOKENS", llm["max_tokens"], int),
        llm_temperature=_env_or_default("TALLEYRAND_LLM_TEMPERATURE", llm["temperature"], float),
        llm_timeout_seconds=_env_or_default("TALLEYRAND_LLM_TIMEOUT_SECONDS", llm["timeout_seconds"], int),
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

    return errors
