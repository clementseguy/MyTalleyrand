#!/usr/bin/env bash
set -euo pipefail

INSTALL_BASE="${INSTALL_BASE:-$HOME/Applications/MyTalleyrandCoach}"
COACH_DIR="$INSTALL_BASE/coach"

if [[ ! -d "$COACH_DIR" ]]; then
  echo "MyTalleyrand Coach introuvable dans $COACH_DIR"
  echo "Lancez d'abord ./scripts/install_macos.sh depuis le dépôt."
  exit 1
fi

cd "$COACH_DIR"
exec .venv/bin/python src/main.py
