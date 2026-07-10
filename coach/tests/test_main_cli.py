from __future__ import annotations

import argparse

from src.main import apply_cli_overrides


def test_debug_cli_forces_analysis_every_turn(monkeypatch):
    monkeypatch.delenv("TALLEYRAND_ANALYSIS_INTERVAL_TURNS", raising=False)
    args = argparse.Namespace(
        debug=True,
        interval=None,
        llm_provider=None,
        llm_model=None,
    )

    apply_cli_overrides(args)

    assert "TALLEYRAND_ANALYSIS_INTERVAL_TURNS" in __import__("os").environ
    assert __import__("os").environ["TALLEYRAND_ANALYSIS_INTERVAL_TURNS"] == "1"


def test_interval_cli_overrides_config_without_debug(monkeypatch):
    monkeypatch.delenv("TALLEYRAND_ANALYSIS_INTERVAL_TURNS", raising=False)
    args = argparse.Namespace(
        debug=False,
        interval=3,
        llm_provider="openai",
        llm_model="gpt-test",
    )

    apply_cli_overrides(args)

    import os

    assert os.environ["TALLEYRAND_ANALYSIS_INTERVAL_TURNS"] == "3"
    assert os.environ["TALLEYRAND_LLM_PROVIDER"] == "openai"
    assert os.environ["TALLEYRAND_LLM_MODEL"] == "gpt-test"
