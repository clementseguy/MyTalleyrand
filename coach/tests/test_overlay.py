from __future__ import annotations

from pathlib import Path

from src.llm_client import LLMAdvice
from src.overlay import TalleyrandOverlay


def test_overlay_persists_position_and_visibility(tmp_path: Path):
    state_file = tmp_path / "overlay_state.json"
    overlay = TalleyrandOverlay(state_file=state_file)

    overlay.move_to(120, 340)
    overlay.toggle_visibility()

    restored = TalleyrandOverlay(state_file=state_file)
    assert restored.position.x == 120
    assert restored.position.y == 340
    assert restored.visible is False


def test_overlay_renders_objective_and_actions(tmp_path: Path):
    overlay = TalleyrandOverlay(state_file=tmp_path / "state.json")
    advice = LLMAdvice(
        objective_10_turns="Sécuriser 2 universités.",
        priority_actions=["Action A", "Action B", "Action C"],
        risks=["Risque"],
        confidence=80,
        categories={"science": ["A"]},
    )

    overlay.show_advice(advice)

    assert "Objectif (10 tours)" in overlay.last_rendered_text
    assert "Action A" in overlay.last_rendered_text


def test_overlay_survives_corrupt_state_file(tmp_path: Path):
    state_file = tmp_path / "overlay_state.json"
    state_file.write_text("{bad json", encoding="utf-8")

    overlay = TalleyrandOverlay(state_file=state_file)

    assert overlay.position.x == 30
    assert overlay.visible is True


def test_overlay_renders_status_message(tmp_path: Path):
    overlay = TalleyrandOverlay(state_file=tmp_path / "state.json")

    overlay.show_status(
        "Problème gamestate",
        "gamestate.json est introuvable.",
        "Vérifiez que le mod MyTalleyrand est activé.",
    )

    assert "Problème gamestate" in overlay.last_rendered_text
    assert "Action suggérée" in overlay.last_rendered_text
    assert "mod MyTalleyrand" in overlay.last_rendered_text


def test_overlay_keeps_fallback_explanation_with_local_advice(tmp_path: Path):
    overlay = TalleyrandOverlay(state_file=tmp_path / "state.json")
    advice = LLMAdvice(
        objective_10_turns="Tenir la position.",
        priority_actions=["Action A", "Action B", "Action C"],
        risks=[],
        confidence=70,
        categories={},
        source="local_fallback",
    )

    overlay.show_advice(advice)

    assert "Fallback LLM activé" in overlay.last_rendered_text
    assert "prochain tour analysé" in overlay.last_rendered_text
    assert "Action A" in overlay.last_rendered_text


def test_overlay_persists_minimized_state_until_next_advice(tmp_path: Path):
    state_file = tmp_path / "overlay_state.json"
    overlay = TalleyrandOverlay(state_file=state_file)

    overlay.minimize()
    restored = TalleyrandOverlay(state_file=state_file)

    assert restored.visible is True
    assert restored.minimized is True

    restored.show_advice(
        LLMAdvice(
            objective_10_turns="Relancer l'économie.",
            priority_actions=["Action A", "Action B", "Action C"],
            risks=[],
            confidence=75,
            categories={},
        )
    )

    assert restored.minimized is False


def test_overlay_hide_does_not_clear_rendered_advice(tmp_path: Path):
    overlay = TalleyrandOverlay(state_file=tmp_path / "state.json")
    advice = LLMAdvice(
        objective_10_turns="Construire une bibliothèque.",
        priority_actions=["Action A", "Action B", "Action C"],
        risks=["Risque A"],
        confidence=80,
        categories={"science": ["Action A"]},
    )

    overlay.show_advice(advice)
    overlay.hide()

    assert overlay.visible is False
    assert "Construire une bibliothèque" in overlay.last_rendered_text
    assert "Risque A" in overlay.last_rendered_text


def test_overlay_critical_status_restores_hidden_overlay(tmp_path: Path):
    overlay = TalleyrandOverlay(state_file=tmp_path / "state.json")
    overlay.hide()
    overlay.minimize()

    overlay.show_status("Erreur critique", "LLM indisponible.", "Vérifiez la clé API.")

    assert overlay.visible is True
    assert overlay.minimized is False
    assert "Erreur critique" in overlay.last_rendered_text


def test_overlay_non_critical_status_respects_hidden_overlay(tmp_path: Path):
    overlay = TalleyrandOverlay(state_file=tmp_path / "state.json")
    overlay.hide()

    overlay.show_status("Info", "Synchronisation.", "Patientez.", critical=False)

    assert overlay.visible is False


def test_overlay_renders_context_insufficient_explanation(tmp_path: Path):
    overlay = TalleyrandOverlay(state_file=tmp_path / "state.json")
    advice = LLMAdvice(
        objective_10_turns="Attendre davantage de contexte.",
        priority_actions=["Action A", "Action B", "Action C"],
        risks=["Contexte pauvre"],
        confidence=35,
        categories={},
        source="context_insufficient",
    )

    overlay.show_advice(advice)

    assert "Contexte insuffisant" in overlay.last_rendered_text
    assert "certain" in overlay.last_rendered_text
    assert "Action A" in overlay.last_rendered_text


def test_overlay_text_backend_keeps_current_victory_focus(tmp_path: Path):
    overlay = TalleyrandOverlay(state_file=tmp_path / "state.json")

    assert overlay.request_victory_focus("science") == "science"
