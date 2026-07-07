"""Tests pour le module config."""

from __future__ import annotations

import json
from pathlib import Path

from src.config import DEFAULT_SYSTEM_PROMPT, DEFAULT_USER_PROMPT_TEMPLATE, load_config, validate_config


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
        "coach": {"analysis_interval_turns": 10},
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
    assert config.analysis_interval_turns == 10


def test_load_config_with_environment_overrides(tmp_path: Path, monkeypatch):
    settings_path = _settings_template(tmp_path)
    monkeypatch.setenv("TALLEYRAND_LLM_MODEL", "gpt-test")
    monkeypatch.setenv("TALLEYRAND_OVERLAY_WIDTH", "777")
    monkeypatch.setenv("TALLEYRAND_ANALYSIS_INTERVAL_TURNS", "5")

    config = load_config(settings_path)

    assert config.llm_model == "gpt-test"
    assert config.overlay_width == 777
    assert config.analysis_interval_turns == 5


def test_load_config_reads_user_file(tmp_path: Path, monkeypatch):
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

    monkeypatch.setattr("src.config.get_api_key", lambda _provider: None)

    config = load_config(settings_path, user_settings_path=user_settings_path)

    assert config.llm_api_key == "sk-test"
    assert config.llm_system_prompt == "Tu es un coach test."
    assert config.llm_user_prompt_template.startswith("Focus=")


def test_load_config_prefers_env_api_key_over_keychain(tmp_path: Path, monkeypatch):
    settings_path = _settings_template(tmp_path)
    monkeypatch.setenv("TALLEYRAND_OPENAI_API_KEY", "sk-env")
    monkeypatch.setattr("src.config.get_api_key", lambda _provider: "sk-keychain")

    config = load_config(settings_path)

    assert config.llm_api_key == "sk-env"


def test_load_config_reads_api_key_from_keychain(tmp_path: Path, monkeypatch):
    settings_path = _settings_template(tmp_path)
    monkeypatch.delenv("TALLEYRAND_OPENAI_API_KEY", raising=False)
    monkeypatch.setattr("src.config.get_api_key", lambda provider: f"sk-{provider}")

    config = load_config(settings_path)

    assert config.llm_api_key == "sk-openai"


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


def test_load_config_reports_missing_settings_file(tmp_path: Path):
    missing = tmp_path / "missing-settings.json"

    try:
        load_config(missing)
    except Exception as exc:
        assert "introuvable" in str(exc)
        assert str(missing) in str(exc)
    else:
        raise AssertionError("load_config aurait dû refuser un settings.json absent")


def test_load_config_reports_corrupt_settings_file(tmp_path: Path):
    settings_path = tmp_path / "settings.json"
    settings_path.write_text("{bad json", encoding="utf-8")

    try:
        load_config(settings_path)
    except Exception as exc:
        assert "JSON invalide" in str(exc)
        assert str(settings_path) in str(exc)
    else:
        raise AssertionError("load_config aurait dû refuser un settings.json corrompu")


def test_load_config_reports_missing_required_section(tmp_path: Path):
    settings_path = tmp_path / "settings.json"
    settings_path.write_text(json.dumps({"schema_version": "0.1.0"}), encoding="utf-8")

    try:
        load_config(settings_path)
    except Exception as exc:
        assert "section 'paths'" in str(exc)
    else:
        raise AssertionError("load_config aurait dû refuser une section obligatoire absente")


def test_user_example_matches_prompt_constants():
    example_path = Path(__file__).resolve().parents[1] / "config" / "coach.user.example.json"
    payload = json.loads(example_path.read_text(encoding="utf-8"))

    assert payload["llm"]["system_prompt"] == DEFAULT_SYSTEM_PROMPT
    assert payload["llm"]["user_prompt_template"] == DEFAULT_USER_PROMPT_TEMPLATE
