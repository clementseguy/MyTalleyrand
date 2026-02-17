"""Tests du schéma gamestate v0."""

from src.gamestate_schema import SCHEMA_VERSION, validate_gamestate


def test_validate_gamestate_accepts_minimal_payload():
    payload = {
        "schema_version": SCHEMA_VERSION,
        "turn_id": 1,
        "turn_number": 1,
        "timestamp_utc": "2026-01-01T00:00:00Z",
        "player": {"leader": "Napoleon"},
        "resources": {"gold": 50},
    }

    errors = validate_gamestate(payload)

    assert errors == []


def test_validate_gamestate_rejects_missing_and_wrong_types():
    payload = {
        "schema_version": "9.9.9",
        "turn_id": -4,
        "turn_number": "1",
        "timestamp_utc": "2026-01-01T00:00:00Z",
        "player": [],
    }

    errors = validate_gamestate(payload)

    fields = {e.field for e in errors}
    assert "resources" in fields
    assert "turn_number" in fields
    assert "schema_version" in fields
    assert "turn_id" in fields
