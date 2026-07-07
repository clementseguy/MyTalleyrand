#!/usr/bin/env python3
"""Génère coach/config/coach.user.example.json depuis les constantes publiques."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_COACH_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_COACH_DIR))

from src.config import DEFAULT_SYSTEM_PROMPT, DEFAULT_USER_PROMPT_TEMPLATE


def build_example() -> dict[str, dict[str, str]]:
    return {
        "llm": {
            "system_prompt": DEFAULT_SYSTEM_PROMPT,
            "user_prompt_template": DEFAULT_USER_PROMPT_TEMPLATE,
        }
    }


def main() -> int:
    output_path = Path(__file__).resolve().parents[1] / "config" / "coach.user.example.json"
    output_path.write_text(json.dumps(build_example(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
