from __future__ import annotations

import time
from pathlib import Path

from tests.conftest import write_gamestate

from src.gamestate_schema import SCHEMA_VERSION
from src.watcher import GameStateWatcher


def test_watcher_detects_new_turn_and_deduplicates(tmp_path: Path):
    gamestate_file = tmp_path / "gamestate.json"
    events: list[int] = []

    def callback(payload, _source):
        events.append(payload["turn_id"])

    watcher = GameStateWatcher(gamestate_file=gamestate_file, callback=callback, poll_interval_seconds=0.05)
    watcher.start()
    try:
        write_gamestate(gamestate_file, turn_id=1, turn_number=1)
        time.sleep(0.2)

        # Même turn_id: ne doit pas déclencher une seconde fois.
        write_gamestate(gamestate_file, turn_id=1, turn_number=1)
        time.sleep(0.2)

        write_gamestate(gamestate_file, turn_id=2, turn_number=2)
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


def test_watcher_reports_missing_file_issue_once(tmp_path: Path):
    gamestate_file = tmp_path / "missing" / "gamestate.json"
    issues = []

    watcher = GameStateWatcher(
        gamestate_file=gamestate_file,
        callback=lambda _payload, _source: None,
        issue_callback=lambda issue, _source: issues.append(issue),
        poll_interval_seconds=0.05,
    )
    watcher.start()
    try:
        time.sleep(0.2)
    finally:
        watcher.stop()

    assert len(issues) == 1
    assert issues[0].kind == "missing"
    assert "mod MyTalleyrand" in issues[0].suggestion


def test_watcher_reports_invalid_schema_issue(tmp_path: Path):
    gamestate_file = tmp_path / "gamestate.json"
    issues = []

    gamestate_file.write_text(
        '{"schema_version":"0.1.0","turn_id":1}',
        encoding="utf-8",
    )
    watcher = GameStateWatcher(
        gamestate_file=gamestate_file,
        callback=lambda _payload, _source: None,
        issue_callback=lambda issue, _source: issues.append(issue),
        poll_interval_seconds=0.05,
    )
    watcher.start()
    try:
        time.sleep(0.2)
    finally:
        watcher.stop()

    assert len(issues) == 1
    assert issues[0].kind == "invalid_schema"
    assert "resources" in issues[0].message


def test_watcher_reports_empty_gamestate_issue(tmp_path: Path):
    gamestate_file = tmp_path / "gamestate.json"
    issues = []
    gamestate_file.write_text("", encoding="utf-8")

    watcher = GameStateWatcher(
        gamestate_file=gamestate_file,
        callback=lambda _payload, _source: None,
        issue_callback=lambda issue, _source: issues.append(issue),
        poll_interval_seconds=0.05,
    )
    watcher.start()
    try:
        time.sleep(0.2)
    finally:
        watcher.stop()

    assert len(issues) == 1
    assert issues[0].kind == "invalid_json"
    assert "vide" in issues[0].message
