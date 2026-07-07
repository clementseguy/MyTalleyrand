"""Fixtures et factories partagées pour les tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.gamestate_schema import SCHEMA_VERSION


def make_gamestate(
    turn_id: int = 1,
    turn_number: int = 1,
    gold: int = 50,
    science: int = 15,
    rich: bool = False,
) -> dict:
    """Crée un payload gamestate minimal valide."""
    payload = {
        "schema_version": SCHEMA_VERSION,
        "turn_id": turn_id,
        "turn_number": turn_number,
        "timestamp_utc": "2026-01-01T00:00:00Z",
        "player": {"leader": "Napoleon"},
        "resources": {"gold": gold, "science": science},
    }
    if rich:
        payload.update(
            {
                "game_parameters": {"difficulty": "Roi", "map_size": "Standard", "game_speed": "Standard"},
                "cities": [{"id": 1, "name": "Paris", "population": 3, "production": "Monument"}],
                "units": [{"id": 1, "type": "UNIT_WARRIOR", "x": 4, "y": 7, "moves": 2}],
            }
        )
    return payload


def write_gamestate(path: Path, turn_id: int = 1, turn_number: int = 1, **kwargs) -> None:
    """Écrit un fichier gamestate.json valide."""
    path.write_text(json.dumps(make_gamestate(turn_id, turn_number, **kwargs)), encoding="utf-8")
