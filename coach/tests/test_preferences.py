from __future__ import annotations

import json
from pathlib import Path

from src.preferences import PreferencesStore, detect_game_parameters, normalize_victory_focus


def test_preferences_store_persists_victory_focus_and_game_parameters(tmp_path: Path):
    store = PreferencesStore(tmp_path / "user_preferences.json")
    prefs = store.load()
    prefs.victory_focus = "science"

    updated = store.update_from_game_state(
        {
            "game": {"difficulty": "Empereur", "map_size": "Standard", "game_speed": "Rapide"},
        },
        prefs,
    )

    payload = json.loads((tmp_path / "user_preferences.json").read_text(encoding="utf-8"))
    assert updated.victory_focus == "science"
    assert payload["game_parameters"]["difficulty"] == "Empereur"
    assert payload["game_parameters"]["map_size"] == "Standard"
    assert payload["game_parameters"]["game_speed"] == "Rapide"


def test_detect_game_parameters_accepts_alternate_export_keys():
    params = detect_game_parameters(
        {
            "settings": {
                "handicap": "Immortel",
                "world_size": "Grande",
                "speed_name": "Standard",
            }
        }
    )

    assert params.difficulty == "Immortel"
    assert params.map_size == "Grande"
    assert params.game_speed == "Standard"


def test_normalize_victory_focus_falls_back_to_balanced():
    assert normalize_victory_focus("score") == "score"
    assert normalize_victory_focus("unknown") == "équilibrée"
