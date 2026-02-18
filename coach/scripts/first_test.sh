#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

TMP_DIR="$(mktemp -d)"
GAMESTATE_FILE="$TMP_DIR/gamestate.json"
EXPORT_DIR="$TMP_DIR/export"
mkdir -p "$EXPORT_DIR"

cat > "$GAMESTATE_FILE" <<'JSON'
{
  "schema_version": "0.1.0",
  "turn_id": 1,
  "turn_number": 1,
  "timestamp_utc": "2026-01-01T00:00:00Z",
  "player": {"leader": "Napoleon"},
  "resources": {"gold": 50, "science": 15}
}
JSON

export TALLEYRAND_GAMESTATE_FILE="$GAMESTATE_FILE"
export TALLEYRAND_EXPORT_DIR="$EXPORT_DIR"
export TALLEYRAND_LOG_FILE="$TMP_DIR/talleyrand.log"

echo "▶️ Lancement coach en mode --once"
python3 -m src.main --once --victory-focus science

echo "🔎 Vérification des artefacts"
test -f "$EXPORT_DIR/coach_history.json"
test -f "$EXPORT_DIR/overlay_state.json" || true

echo "✅ Smoke test réussi"
