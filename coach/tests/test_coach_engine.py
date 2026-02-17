from __future__ import annotations

import json
from pathlib import Path

from src.coach import CoachingEngine
from src.llm_client import LLMClient


def _payload(turn_id: int, turn_number: int) -> dict:
    return {
        "schema_version": "0.1.0",
        "turn_id": turn_id,
        "turn_number": turn_number,
        "timestamp_utc": "2026-01-01T00:00:00Z",
        "player": {"leader": "Napoleon"},
        "resources": {"gold": 80, "science": 12},
    }


def test_coaching_engine_triggers_turn_1_and_10(tmp_path: Path):
    history_file = tmp_path / "history.json"
    engine = CoachingEngine(LLMClient("mock", "mock"), history_file=history_file)

    assert engine.maybe_generate_advice(_payload(1, 1)) is not None
    assert engine.maybe_generate_advice(_payload(2, 2)) is None
    assert engine.maybe_generate_advice(_payload(10, 10)) is not None

    history = json.loads(history_file.read_text(encoding="utf-8"))
    assert [entry["turn_number"] for entry in history] == [1, 10]


def test_coaching_engine_persists_victory_focus(tmp_path: Path):
    history_file = tmp_path / "history.json"
    engine = CoachingEngine(LLMClient("mock", "mock"), history_file=history_file)
    engine.set_victory_focus("culture")

    advice = engine.maybe_generate_advice(_payload(1, 1))

    assert advice is not None
    history = json.loads(history_file.read_text(encoding="utf-8"))
    assert history[0]["victory_focus"] == "culture"
