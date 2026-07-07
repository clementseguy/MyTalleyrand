from __future__ import annotations

import json
from pathlib import Path

from tests.conftest import make_gamestate

from src.coach import CoachingEngine
from src.llm_client import LLMClient


def test_coaching_engine_triggers_turn_1_and_10(tmp_path: Path):
    history_file = tmp_path / "history.json"
    engine = CoachingEngine(LLMClient("mock", "mock"), history_file=history_file)

    assert engine.maybe_generate_advice(make_gamestate(turn_id=1, turn_number=1)) is not None
    assert engine.maybe_generate_advice(make_gamestate(turn_id=2, turn_number=2)) is None
    assert engine.maybe_generate_advice(make_gamestate(turn_id=10, turn_number=10)) is not None

    history = json.loads(history_file.read_text(encoding="utf-8"))
    assert [entry["turn_number"] for entry in history] == [1, 10]


def test_coaching_engine_persists_victory_focus(tmp_path: Path):
    history_file = tmp_path / "history.json"
    engine = CoachingEngine(LLMClient("mock", "mock"), history_file=history_file)
    engine.set_victory_focus("culture")

    advice = engine.maybe_generate_advice(make_gamestate(turn_id=1, turn_number=1))

    assert advice is not None
    history = json.loads(history_file.read_text(encoding="utf-8"))
    assert history[0]["victory_focus"] == "culture"


def test_coaching_engine_survives_corrupt_history(tmp_path: Path):
    history_file = tmp_path / "history.json"
    history_file.write_text("{corrupted", encoding="utf-8")
    engine = CoachingEngine(LLMClient("mock", "mock"), history_file=history_file)

    advice = engine.maybe_generate_advice(make_gamestate(turn_id=1, turn_number=1))

    assert advice is not None
    history = json.loads(history_file.read_text(encoding="utf-8"))
    assert len(history) == 1
