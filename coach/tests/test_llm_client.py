from __future__ import annotations

from tests.conftest import make_gamestate

from src.llm_client import LLMClient


def test_generate_advice_uses_fallback_when_remote_fails(monkeypatch):
    client = LLMClient(provider="openai", model="gpt-4o-mini")

    def boom(*_args, **_kwargs):
        raise RuntimeError("offline")

    monkeypatch.setattr(client, "_generate_remote_advice_raw", boom)

    advice = client.generate_advice(make_gamestate(), victory_focus="science")

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

    advice = client.generate_advice(make_gamestate(), victory_focus="science")

    assert advice.objective_10_turns == remote_payload["objective_10_turns"]
    assert advice.confidence == 82
    assert advice.categories["science"] == ["S1"]


def test_build_prompt_uses_custom_template():
    client = LLMClient(
        provider="openai",
        model="gpt-4o-mini",
        user_prompt_template="F={victory_focus} | G={game_state_json}",
    )

    prompt = client._build_prompt(make_gamestate(), victory_focus="science")

    assert prompt.startswith("F=science")
    assert '"turn_id": 1' in prompt


def test_generate_advice_notifies_fallback_status_when_remote_fails(monkeypatch):
    statuses = []
    client = LLMClient(provider="openai", model="gpt-4o-mini", status_callback=statuses.append)

    def boom(*_args, **_kwargs):
        raise RuntimeError("offline")

    monkeypatch.setattr(client, "_generate_remote_advice_raw", boom)

    advice = client.generate_advice(make_gamestate(), victory_focus="science")

    assert advice.priority_actions
    assert len(statuses) == 1
    assert statuses[0].title == "Fallback LLM activé"
    assert "prochain tour" in statuses[0].suggestion


def test_remote_retry_notifies_reconnection_status():
    statuses = []
    client = LLMClient(provider="openai", model="gpt-4o-mini", status_callback=statuses.append, api_key="test")

    class FailingResponses:
        def create(self, **_kwargs):
            raise TimeoutError("timeout réseau")

    class FailingClient:
        responses = FailingResponses()

    client._openai_client = FailingClient()

    advice = client.generate_advice(make_gamestate(), victory_focus="science")

    assert advice.priority_actions
    assert [status.title for status in statuses[:2]] == [
        "Reconnexion LLM en cours",
        "Reconnexion LLM en cours",
    ]
    assert statuses[-1].title == "Fallback LLM activé"
