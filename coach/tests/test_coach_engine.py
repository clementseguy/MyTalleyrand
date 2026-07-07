from __future__ import annotations

import json
from pathlib import Path

from tests.conftest import make_gamestate

from src.coach import CoachingEngine
from src.llm_client import LLMClient


def test_coaching_engine_triggers_turn_1_and_10(tmp_path: Path):
    history_file = tmp_path / "history.json"
    engine = CoachingEngine(LLMClient("mock", "mock"), history_file=history_file)

    assert engine.maybe_generate_advice(make_gamestate(turn_id=1, turn_number=1, rich=True)) is not None
    assert engine.maybe_generate_advice(make_gamestate(turn_id=2, turn_number=2, rich=True)) is None
    assert engine.maybe_generate_advice(make_gamestate(turn_id=10, turn_number=10, rich=True)) is not None

    history = json.loads(history_file.read_text(encoding="utf-8"))
    assert [entry["turn_number"] for entry in history] == [1, 10]


def test_coaching_engine_persists_victory_focus(tmp_path: Path):
    history_file = tmp_path / "history.json"
    engine = CoachingEngine(LLMClient("mock", "mock"), history_file=history_file)
    engine.set_victory_focus("culture")

    advice = engine.maybe_generate_advice(make_gamestate(turn_id=1, turn_number=1, rich=True))

    assert advice is not None
    history = json.loads(history_file.read_text(encoding="utf-8"))
    assert history[0]["victory_focus"] == "culture"


def test_coaching_engine_survives_corrupt_history(tmp_path: Path):
    history_file = tmp_path / "history.json"
    history_file.write_text("{corrupted", encoding="utf-8")
    engine = CoachingEngine(LLMClient("mock", "mock"), history_file=history_file)

    advice = engine.maybe_generate_advice(make_gamestate(turn_id=1, turn_number=1, rich=True))

    assert advice is not None
    history = json.loads(history_file.read_text(encoding="utf-8"))
    assert len(history) == 1


def test_coaching_engine_persists_detected_game_parameters(tmp_path: Path):
    from src.preferences import PreferencesStore

    history_file = tmp_path / "history.json"
    preferences_store = PreferencesStore(tmp_path / "user_preferences.json")
    engine = CoachingEngine(
        LLMClient("mock", "mock"),
        history_file=history_file,
        preferences_store=preferences_store,
    )
    game_state = make_gamestate(turn_id=10, turn_number=10)
    game_state["game"] = {"difficulty": "Roi", "map_size": "Petite", "game_speed": "Standard"}

    engine.maybe_generate_advice(game_state)

    history = json.loads(history_file.read_text(encoding="utf-8"))
    assert history[0]["game_parameters"] == {
        "difficulty": "Roi",
        "map_size": "Petite",
        "game_speed": "Standard",
    }


def test_coaching_engine_returns_cautious_advice_for_insufficient_context(tmp_path: Path):
    history_file = tmp_path / "history.json"
    engine = CoachingEngine(LLMClient("mock", "mock"), history_file=history_file)
    game_state = make_gamestate(turn_id=1, turn_number=1)
    game_state["cities"] = []

    advice = engine.maybe_generate_advice(game_state)

    assert advice is not None
    assert advice.source == "context_insufficient"
    assert advice.confidence < 50
    assert "contexte" in advice.risks[0].lower()


def test_coaching_engine_uses_configurable_interval(tmp_path: Path):
    history_file = tmp_path / "history.json"
    engine = CoachingEngine(LLMClient("mock", "mock"), history_file=history_file, analysis_interval_turns=5)

    assert engine.maybe_generate_advice(make_gamestate(turn_id=5, turn_number=5, rich=True)) is not None

    history = json.loads(history_file.read_text(encoding="utf-8"))
    assert history[0]["reason"] == "cycle_5_tours"


def test_coaching_engine_changed_focus_updates_next_prompt(tmp_path: Path, monkeypatch):
    history_file = tmp_path / "history.json"
    client = LLMClient("mock", "mock")
    captured = {}

    def capture(game_state, victory_focus):
        captured["victory_focus"] = victory_focus
        return client._generate_fallback_advice(game_state, victory_focus)

    monkeypatch.setattr(client, "generate_advice", capture)
    engine = CoachingEngine(client, history_file=history_file)
    engine.set_victory_focus("culture")

    engine.maybe_generate_advice(make_gamestate(turn_id=10, turn_number=10, rich=True))

    assert captured["victory_focus"].startswith("culture")


def test_coaching_engine_flags_empty_cities_mid_game(tmp_path: Path):
    history_file = tmp_path / "history.json"
    engine = CoachingEngine(LLMClient("mock", "mock"), history_file=history_file)
    game_state = make_gamestate(turn_id=10, turn_number=10, rich=True)
    game_state["cities"] = []

    advice = engine.maybe_generate_advice(game_state)

    assert advice is not None
    assert advice.source == "context_insufficient"
