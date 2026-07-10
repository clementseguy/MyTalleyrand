#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="${1:-$ROOT_DIR/coach/.venv}"

if [[ ! -d "$VENV_DIR" ]]; then
  echo "❌ .venv introuvable: $VENV_DIR"
  exit 1
fi

echo "🔎 Audit secrets du venv: $VENV_DIR"

PATTERN='(^|[^A-Za-z0-9_])sk-[A-Za-z0-9_-]{20,}|Bearer[[:space:]]+[A-Za-z0-9._-]{30,}|(OPENAI|MISTRAL|TALLEYRAND_[A-Z_]+)_API_KEY[[:space:]]*=[[:space:]]*["'\'']?[A-Za-z0-9._-]{20,}["'\'']?'

if rg --hidden --no-ignore --glob '!**/*.pyc' --glob '!**/*.so' --glob '!**/*.dylib' --glob '!**/*.a' -n "$PATTERN" "$VENV_DIR"; then
  echo "❌ Secrets ou marqueurs sensibles potentiels détectés dans le venv."
  echo "   Vérifiez les lignes ci-dessus avant de conserver cet environnement."
  exit 1
fi

echo "✅ Aucun secret détectable par les motifs connus."
