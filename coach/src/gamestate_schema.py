"""Schéma minimal v0 du fichier gamestate.json et validation associée."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

SCHEMA_VERSION = "0.1.0"


@dataclass(frozen=True)
class GameStateSchemaError:
    field: str
    message: str


def validate_gamestate(payload: dict[str, Any]) -> list[GameStateSchemaError]:
    """Valide le format minimal attendu pour le MVP phase 0."""
    errors: list[GameStateSchemaError] = []

    required_fields = {
        "schema_version": str,
        "turn_id": int,
        "turn_number": int,
        "timestamp_utc": str,
        "player": dict,
        "resources": dict,
    }

    for field, expected_type in required_fields.items():
        if field not in payload:
            errors.append(GameStateSchemaError(field, "missing required field"))
            continue
        if not isinstance(payload[field], expected_type):
            errors.append(
                GameStateSchemaError(
                    field,
                    f"expected {expected_type.__name__}, got {type(payload[field]).__name__}",
                )
            )

    schema_version = payload.get("schema_version")
    if isinstance(schema_version, str) and schema_version != SCHEMA_VERSION:
        errors.append(
            GameStateSchemaError(
                "schema_version",
                f"unsupported version '{schema_version}', expected '{SCHEMA_VERSION}'",
            )
        )

    if isinstance(payload.get("turn_id"), int) and payload["turn_id"] < 0:
        errors.append(GameStateSchemaError("turn_id", "must be >= 0"))

    if isinstance(payload.get("turn_number"), int) and payload["turn_number"] <= 0:
        errors.append(GameStateSchemaError("turn_number", "must be > 0"))

    return errors
