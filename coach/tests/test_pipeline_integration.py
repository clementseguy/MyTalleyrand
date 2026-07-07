from __future__ import annotations

import time
from pathlib import Path

from tests.conftest import write_gamestate

from src.coach import CoachingEngine
from src.llm_client import LLMClient
from src.overlay import TalleyrandOverlay
from src.watcher import GameStateWatcher


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
        write_gamestate(gamestate_file, 1, 1)
        time.sleep(0.2)
    finally:
        watcher.stop()

    assert history_file.exists()
    assert "Actions prioritaires" in overlay.last_rendered_text
