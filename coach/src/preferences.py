"""Préférences joueur persistées pour orienter la logique de coaching."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

VICTORY_FOCUSES = ("domination", "science", "culture", "diplomatie", "score", "équilibrée")
DEFAULT_VICTORY_FOCUS = "équilibrée"


@dataclass
class GameParameters:
    """Paramètres de partie détectés depuis le gamestate quand le mod les expose."""

    difficulty: str | None = None
    map_size: str | None = None
    game_speed: str | None = None


@dataclass
class UserPreferences:
    """Préférences non sensibles réutilisées à chaque analyse."""

    victory_focus: str = DEFAULT_VICTORY_FOCUS
    game_parameters: GameParameters = field(default_factory=GameParameters)

    def normalized_focus(self) -> str:
        return normalize_victory_focus(self.victory_focus)


def normalize_victory_focus(focus: str | None) -> str:
    normalized = (focus or DEFAULT_VICTORY_FOCUS).strip().lower()
    aliases = {
        "diplomacy": "diplomatie",
        "balanced": "équilibrée",
        "equilibree": "équilibrée",
        "équilibré": "équilibrée",
    }
    normalized = aliases.get(normalized, normalized)
    if normalized not in VICTORY_FOCUSES:
        logger.warning("Objectif de victoire inconnu '%s', fallback équilibrée", focus)
        return DEFAULT_VICTORY_FOCUS
    return normalized


class PreferencesStore:
    """Charge et sauvegarde les préférences joueur dans un JSON dédié."""

    def __init__(self, preferences_file: Path):
        self.preferences_file = preferences_file

    def load(self) -> UserPreferences:
        if not self.preferences_file.exists():
            return UserPreferences()
        try:
            payload = json.loads(self.preferences_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Préférences utilisateur illisibles, réinitialisation (%s)", exc)
            return UserPreferences()
        if not isinstance(payload, dict):
            return UserPreferences()

        game_parameters = payload.get("game_parameters", {})
        if not isinstance(game_parameters, dict):
            game_parameters = {}
        return UserPreferences(
            victory_focus=normalize_victory_focus(str(payload.get("victory_focus", DEFAULT_VICTORY_FOCUS))),
            game_parameters=GameParameters(
                difficulty=_optional_text(game_parameters.get("difficulty")),
                map_size=_optional_text(game_parameters.get("map_size")),
                game_speed=_optional_text(game_parameters.get("game_speed")),
            ),
        )

    def save(self, preferences: UserPreferences) -> None:
        self.preferences_file.parent.mkdir(parents=True, exist_ok=True)
        preferences.victory_focus = preferences.normalized_focus()
        self.preferences_file.write_text(
            json.dumps(asdict(preferences), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def update_from_game_state(self, game_state: dict[str, Any], preferences: UserPreferences) -> UserPreferences:
        detected = detect_game_parameters(game_state)
        merged = GameParameters(
            difficulty=detected.difficulty or preferences.game_parameters.difficulty,
            map_size=detected.map_size or preferences.game_parameters.map_size,
            game_speed=detected.game_speed or preferences.game_parameters.game_speed,
        )
        updated = UserPreferences(victory_focus=preferences.normalized_focus(), game_parameters=merged)
        self.save(updated)
        return updated


def detect_game_parameters(game_state: dict[str, Any]) -> GameParameters:
    candidates = [
        game_state.get("game"),
        game_state.get("settings"),
        game_state.get("game_parameters"),
    ]
    merged: dict[str, Any] = {}
    for candidate in candidates:
        if isinstance(candidate, dict):
            merged.update(candidate)
    return GameParameters(
        difficulty=_optional_text(_first_present(merged, "difficulty", "difficulty_name", "handicap")),
        map_size=_optional_text(_first_present(merged, "map_size", "world_size", "map")),
        game_speed=_optional_text(_first_present(merged, "game_speed", "speed", "speed_name")),
    )


def _first_present(payload: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = payload.get(key)
        if value not in (None, ""):
            return value
    return None


def _optional_text(value: Any) -> str | None:
    if value in (None, ""):
        return None
    return str(value).strip() or None
