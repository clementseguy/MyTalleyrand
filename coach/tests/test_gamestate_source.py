"""Tests de la source SQLite ModUserData et de son intégration au watcher."""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path

from tests.conftest import make_gamestate

from src.gamestate_source import (
    FileGameStateSource,
    SqliteModUserDataSource,
    build_source,
)
from src.watcher import GameStateWatcher


def _write_userdata_db(
    path: Path,
    *,
    gamestate: dict | None = None,
    write_seq: int | None = None,
    extra: dict | None = None,
) -> None:
    """Reproduit la base ModUserData écrite par le mod (table SimpleValues)."""
    conn = sqlite3.connect(str(path))
    try:
        conn.execute("CREATE TABLE IF NOT EXISTS SimpleValues(Name TEXT PRIMARY KEY, Value VARIANT)")
        rows: list[tuple[str, object]] = []
        if gamestate is not None:
            rows.append(("gamestate_json", json.dumps(gamestate)))
        if write_seq is not None:
            rows.append(("write_seq", write_seq))
        for name, value in (extra or {}).items():
            rows.append((name, value))
        conn.executemany(
            "INSERT OR REPLACE INTO SimpleValues(Name, Value) VALUES(?, ?)", rows
        )
        conn.commit()
    finally:
        conn.close()


def test_sqlite_source_reads_gamestate(tmp_path: Path):
    db = tmp_path / "mod-1.db"
    _write_userdata_db(db, gamestate=make_gamestate(turn_id=5, turn_number=5), write_seq=5)

    source = SqliteModUserDataSource(db)
    snapshot = source.read()

    assert snapshot.exists is True
    assert snapshot.change_token is not None
    assert json.loads(snapshot.raw_json)["turn_id"] == 5
    # Jeton dérivé du contenu : stable tant que le gamestate ne change pas.
    assert source.read().change_token == snapshot.change_token


def test_sqlite_source_token_follows_content_not_write_seq(tmp_path: Path):
    """Anti-régression : le jeton suit le gamestate, pas write_seq.

    Simule la course d'écriture : write_seq avance mais le gamestate reste au
    tour précédent -> le jeton NE doit PAS changer (sinon on saute un tour)."""
    db = tmp_path / "mod-1.db"
    _write_userdata_db(db, gamestate=make_gamestate(turn_id=6, turn_number=6), write_seq=6)
    token_before = SqliteModUserDataSource(db).read().change_token

    # write_seq passe à 7 mais gamestate encore au tour 6 (état transitoire).
    _write_userdata_db(db, gamestate=make_gamestate(turn_id=6, turn_number=6), write_seq=7)
    assert SqliteModUserDataSource(db).read().change_token == token_before

    # gamestate passe réellement au tour 7 -> le jeton change.
    _write_userdata_db(db, gamestate=make_gamestate(turn_id=7, turn_number=7), write_seq=7)
    assert SqliteModUserDataSource(db).read().change_token != token_before


def test_sqlite_source_missing_db(tmp_path: Path):
    snapshot = SqliteModUserDataSource(tmp_path / "absent.db").read()
    assert snapshot.exists is False
    assert snapshot.raw_json is None


def test_sqlite_source_present_but_no_gamestate_yet(tmp_path: Path):
    db = tmp_path / "mod-1.db"
    # Base ouverte par le mod au chargement, avant tout tour (pas de gamestate_json).
    _write_userdata_db(db, extra={"loaded_at_turn": 0})

    snapshot = SqliteModUserDataSource(db).read()
    assert snapshot.exists is True
    assert snapshot.raw_json is None


def test_watcher_with_sqlite_source_detects_and_deduplicates(tmp_path: Path):
    db = tmp_path / "mod-1.db"
    events: list[int] = []

    watcher = GameStateWatcher(
        db,
        callback=lambda payload, _src: events.append(payload["turn_id"]),
        poll_interval_seconds=0.05,
        source=SqliteModUserDataSource(db),
    )
    watcher.start()
    try:
        _write_userdata_db(db, gamestate=make_gamestate(turn_id=1, turn_number=1), write_seq=1)
        time.sleep(0.2)

        # Même write_seq -> aucun changement -> pas de nouveau déclenchement.
        time.sleep(0.15)

        # Nouveau tour : write_seq incrémenté.
        _write_userdata_db(db, gamestate=make_gamestate(turn_id=2, turn_number=2), write_seq=2)
        time.sleep(0.2)
    finally:
        watcher.stop()

    assert events == [1, 2]


def test_watcher_with_sqlite_source_ignores_invalid_json(tmp_path: Path):
    db = tmp_path / "mod-1.db"
    triggered = False

    def callback(_payload, _src):
        nonlocal triggered
        triggered = True

    watcher = GameStateWatcher(
        db,
        callback=callback,
        poll_interval_seconds=0.05,
        source=SqliteModUserDataSource(db),
    )
    watcher.start()
    try:
        _write_userdata_db(db, extra={"gamestate_json": "{bad json", "write_seq": 1})
        time.sleep(0.2)
    finally:
        watcher.stop()

    assert triggered is False


def test_build_source_selects_implementation(tmp_path: Path):
    db = tmp_path / "mod-1.db"
    file = tmp_path / "gamestate.json"

    assert isinstance(build_source("sqlite", db_path=db, file_path=file), SqliteModUserDataSource)
    assert isinstance(build_source("file", db_path=db, file_path=file), FileGameStateSource)
    # Défaut robuste : tout ce qui n'est pas 'file' -> sqlite.
    assert isinstance(build_source("autre", db_path=db, file_path=file), SqliteModUserDataSource)
