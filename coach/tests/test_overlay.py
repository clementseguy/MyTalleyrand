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
