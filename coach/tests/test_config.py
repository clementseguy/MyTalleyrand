"""Tests pour le module config."""

from __future__ import annotations

import json
from pathlib import Path

from src.config import load_config, validate_config


def _settings_template(tmp_path: Path) -> Path:
    settings = {
        "schema_version": "0.1.0",
        "paths": {
            "civ5_user_dir": str(tmp_path / "civ5"),
            "mod_export_dir": str(tmp_path / "export"),
            "gamestate_file": str(tmp_path / "export" / "gamestate.json"),
            "log_file": str(tmp_path / "logs" / "app.log"),
        },
        "llm": {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "max_tokens": 500,
            "temperature": 0.7,
            "timeout_seconds": 15,
        },
        "overlay": {"width": 400, "height": 600, "opacity": 0.9},
    }
    settings_path = tmp_path / "settings.json"
    settings_path.write_text(json.dumps(settings), encoding="utf-8")
    return settings_path


def test_load_config_reads_json(tmp_path: Path):
    settings_path = _settings_template(tmp_path)

    config = load_config(settings_path)

    assert config.schema_version == "0.1.0"
    assert config.llm_provider == "openai"
    assert config.overlay_width == 400


def test_load_config_with_environment_overrides(tmp_path: Path, monkeypatch):
    settings_path = _settings_template(tmp_path)
    monkeypatch.setenv("TALLEYRAND_LLM_MODEL", "gpt-test")
    monkeypatch.setenv("TALLEYRAND_OVERLAY_WIDTH", "777")

    config = load_config(settings_path)

    assert config.llm_model == "gpt-test"
    assert config.overlay_width == 777


def test_load_config_reads_user_file(tmp_path: Path):
    settings_path = _settings_template(tmp_path)
    user_settings_path = tmp_path / "coach.user.json"
    user_settings_path.write_text(
        json.dumps(
            {
                "llm": {
                    "api_key": "sk-test",
                    "system_prompt": "Tu es un coach test.",
                    "user_prompt_template": "Focus={victory_focus}; State={game_state_json}",
                }
            }
        ),
        encoding="utf-8",
    )

    config = load_config(settings_path, user_settings_path=user_settings_path)

    assert config.llm_api_key == "sk-test"
    assert config.llm_system_prompt == "Tu es un coach test."
    assert config.llm_user_prompt_template.startswith("Focus=")


def test_validate_config_rejects_invalid_values(tmp_path: Path):
    settings_path = _settings_template(tmp_path)
    config = load_config(settings_path)
    bad_config = config.__class__(**{**config.__dict__, "overlay_opacity": 1.4})

    errors = validate_config(bad_config)

    assert errors
    assert "Overlay opacity must be in (0, 1]" in errors


def test_validate_config_rejects_invalid_prompt_template(tmp_path: Path):
    settings_path = _settings_template(tmp_path)
    config = load_config(settings_path)
    bad_config = config.__class__(
        **{**config.__dict__, "llm_user_prompt_template": "Focus only = {victory_focus}"}
    )

    errors = validate_config(bad_config)

    assert "LLM user prompt template must include {game_state_json}" in errors
