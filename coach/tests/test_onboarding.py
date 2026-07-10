"""Tests pour l'onboarding de premier lancement."""

from __future__ import annotations

from pathlib import Path

from src.onboarding import (
    build_onboarding_checks,
    format_onboarding_report,
    mark_onboarding_done,
    should_run_first_launch_onboarding,
)
from tests.test_config import _settings_template
from src.config import load_config


def test_onboarding_reports_missing_civ5_dir_and_writable_export(tmp_path: Path, monkeypatch):
    settings_path = _settings_template(tmp_path)
    monkeypatch.delenv("TALLEYRAND_LLM_PROVIDER", raising=False)
    monkeypatch.setattr("src.config.get_api_key", lambda _provider: None)
    monkeypatch.setattr("src.onboarding.platform.system", lambda: "Linux")
    config = load_config(settings_path)

    checks = build_onboarding_checks(config)

    assert [check.name for check in checks] == ["Dossier Civ5", "Dossier état coach", "Clé API Mistral"]
    assert checks[0].ok is False
    assert checks[1].ok is True
    assert checks[2].ok is False
    assert "TALLEYRAND_CIV5_DIR" in checks[0].suggestion
    assert "src.keychain set mistral" in checks[2].suggestion


def test_onboarding_report_includes_failed_actions(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("TALLEYRAND_LLM_PROVIDER", raising=False)
    config = load_config(_settings_template(tmp_path))
    monkeypatch.setattr("src.onboarding.platform.system", lambda: "Linux")

    report = format_onboarding_report(build_onboarding_checks(config))

    assert "Onboarding MyTalleyrand" in report
    assert "⚠️ Dossier Civ5" in report
    assert "Action:" in report


def test_onboarding_marker_lifecycle(tmp_path: Path):
    config = load_config(_settings_template(tmp_path))

    assert should_run_first_launch_onboarding(config) is True

    mark_onboarding_done(config)

    assert should_run_first_launch_onboarding(config) is False
