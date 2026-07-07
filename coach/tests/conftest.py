"""Fixtures et factories partagées pour les tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.gamestate_schema import SCHEMA_VERSION


def make_gamestate(turn_id: int = 1, turn_number: int = 1, gold: int = 50, science: int = 15) -> dict:
    """Crée un payload gamestate minimal valide."""
    return {
        "schema_version": SCHEMA_VERSION,
        "turn_id": turn_id,
        "turn_number": turn_number,
        "timestamp_utc": "2026-01-01T00:00:00Z",
        "player": {"leader": "Napoleon"},
        "resources": {"gold": gold, "science": science},
    }


def write_gamestate(path: Path, turn_id: int = 1, turn_number: int = 1, **kwargs) -> None:
    """Écrit un fichier gamestate.json valide."""
    path.write_text(json.dumps(make_gamestate(turn_id, turn_number, **kwargs)), encoding="utf-8")
