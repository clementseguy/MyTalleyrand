from __future__ import annotations

import json
import time
from pathlib import Path

from src.gamestate_schema import SCHEMA_VERSION
from src.watcher import GameStateWatcher


def _write_state(path: Path, turn_id: int, turn_number: int):
    payload = {
        "schema_version": SCHEMA_VERSION,
        "turn_id": turn_id,
        "turn_number": turn_number,
        "timestamp_utc": "2026-01-01T00:00:00Z",
        "player": {"leader": "Napoleon"},
        "resources": {"gold": 50, "science": 15},
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_watcher_detects_new_turn_and_deduplicates(tmp_path: Path):
    gamestate_file = tmp_path / "gamestate.json"
    events: list[int] = []

    def callback(payload, _source):
        events.append(payload["turn_id"])

    watcher = GameStateWatcher(gamestate_file=gamestate_file, callback=callback, poll_interval_seconds=0.05)
    watcher.start()
    try:
        _write_state(gamestate_file, turn_id=1, turn_number=1)
        time.sleep(0.2)

        # Même turn_id: ne doit pas déclencher une seconde fois.
        _write_state(gamestate_file, turn_id=1, turn_number=1)
        time.sleep(0.2)

        _write_state(gamestate_file, turn_id=2, turn_number=2)
        time.sleep(0.2)
    finally:
        watcher.stop()

    assert events == [1, 2]


def test_watcher_ignores_invalid_json(tmp_path: Path):
    gamestate_file = tmp_path / "gamestate.json"
    triggered = False

    def callback(_payload, _source):
        nonlocal triggered
        triggered = True

    watcher = GameStateWatcher(gamestate_file=gamestate_file, callback=callback, poll_interval_seconds=0.05)
    watcher.start()
    try:
        gamestate_file.write_text("{bad json", encoding="utf-8")
        time.sleep(0.2)
    finally:
        watcher.stop()

    assert triggered is False
