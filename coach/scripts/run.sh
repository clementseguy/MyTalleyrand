#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ ! -x ".venv/bin/python" ]]; then
  echo "❌ Environnement Python local introuvable ou cassé: $(pwd)/.venv/bin/python"
  echo "   Recréez-le avec:"
  echo "     python3 -m venv .venv"
  echo "     .venv/bin/python -m pip install -r requirements.txt"
  exit 1
fi

exec .venv/bin/python src/main.py "$@"
