from __future__ import annotations

from src.llm_client import LLMClient


def _payload() -> dict:
    return {
        "schema_version": "0.1.0",
        "turn_id": 1,
        "turn_number": 1,
        "timestamp_utc": "2026-01-01T00:00:00Z",
        "player": {"leader": "Napoleon"},
        "resources": {"gold": 60, "science": 10},
    }


def test_generate_advice_uses_fallback_when_remote_fails(monkeypatch):
    client = LLMClient(provider="openai", model="gpt-4o-mini")

    def boom(*_args, **_kwargs):
        raise RuntimeError("offline")

    monkeypatch.setattr(client, "_generate_remote_advice_raw", boom)

    advice = client.generate_advice(_payload(), victory_focus="science")

    assert "tour 11" in advice.objective_10_turns
    assert 3 <= len(advice.priority_actions) <= 5


def test_generate_advice_parses_remote_payload(monkeypatch):
    client = LLMClient(provider="openai", model="gpt-4o-mini")
    remote_payload = {
        "objective_10_turns": "Prendre l'avantage scientifique.",
        "priority_actions": ["A", "B", "C"],
        "risks": ["R1"],
        "confidence": 82,
        "categories": {
            "economie": ["E1"],
            "science": ["S1"],
            "militaire": ["M1"],
            "diplomatie": ["D1"],
        },
    }

    monkeypatch.setattr(
        client,
        "_generate_remote_advice_raw",
        lambda *_args, **_kwargs: remote_payload,
    )

    advice = client.generate_advice(_payload(), victory_focus="science")

    assert advice.objective_10_turns == remote_payload["objective_10_turns"]
    assert advice.confidence == 82
    assert advice.categories["science"] == ["S1"]


def test_build_prompt_uses_custom_template():
    client = LLMClient(
        provider="openai",
        model="gpt-4o-mini",
        user_prompt_template="F={victory_focus} | G={game_state_json}",
    )

    prompt = client._build_prompt(_payload(), victory_focus="science")

    assert prompt.startswith("F=science")
    assert '"turn_id": 1' in prompt
