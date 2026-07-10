#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
COACH_DIR="$ROOT_DIR/coach"
VENV_PY="$COACH_DIR/.venv/bin/python"

if [[ ! -x "$VENV_PY" ]]; then
  echo "❌ Environnement Python local introuvable ou cassé: $VENV_PY"
  echo "   Recréez-le depuis le dépôt courant:"
  echo "     cd \"$COACH_DIR\""
  echo "     python3 -m venv .venv"
  echo "     .venv/bin/python -m pip install -r requirements.txt"
  exit 1
fi

cd "$COACH_DIR"
exec "$VENV_PY" src/main.py "$@"
