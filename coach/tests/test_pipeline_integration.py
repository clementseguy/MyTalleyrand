from __future__ import annotations

import json
import time
from pathlib import Path

from src.coach import CoachingEngine
from src.llm_client import LLMClient
from src.overlay import TalleyrandOverlay
from src.watcher import GameStateWatcher


def _write_state(path: Path, turn_id: int, turn_number: int):
    payload = {
        "schema_version": "0.1.0",
        "turn_id": turn_id,
        "turn_number": turn_number,
        "timestamp_utc": "2026-01-01T00:00:00Z",
        "player": {"leader": "Napoleon"},
        "resources": {"gold": 50, "science": 15},
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_end_to_end_watcher_to_overlay(tmp_path: Path):
    gamestate_file = tmp_path / "gamestate.json"
    history_file = tmp_path / "history.json"
    overlay = TalleyrandOverlay(state_file=tmp_path / "overlay.json")
    engine = CoachingEngine(LLMClient("mock", "mock"), history_file=history_file)

    def callback(payload, _source):
        advice = engine.maybe_generate_advice(payload)
        if advice:
            overlay.show_advice(advice)

    watcher = GameStateWatcher(gamestate_file=gamestate_file, callback=callback, poll_interval_seconds=0.05)
    watcher.start()
    try:
        _write_state(gamestate_file, 1, 1)
        time.sleep(0.2)
    finally:
        watcher.stop()

    assert history_file.exists()
    assert "Actions prioritaires" in overlay.last_rendered_text
