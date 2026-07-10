#!/usr/bin/env bash
set -euo pipefail

CIV5_DIR="${CIV5_DOCS_DIR:-$HOME/Library/Application Support/Sid Meier's Civilization 5}"
CONFIG_FILE="$CIV5_DIR/config.ini"
CACHE_DIR="$CIV5_DIR/cache"

if [[ ! -d "$CIV5_DIR" ]]; then
  echo "❌ Dossier Civ5 introuvable: $CIV5_DIR"
  echo "   Lancez Civilization V au moins une fois ou définissez CIV5_DOCS_DIR."
  exit 1
fi

if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "❌ config.ini introuvable: $CONFIG_FILE"
  echo "   Lancez Civilization V une première fois, fermez-le, puis relancez ce script."
  exit 1
fi

chmod u+w "$CONFIG_FILE" 2>/dev/null || true

set_flag() {
  local key="$1"
  local value="$2"
  if grep -q "^$key =" "$CONFIG_FILE"; then
    sed -i '' -e "s/^$key = .*/$key = $value/" "$CONFIG_FILE"
  else
    printf '%s = %s\n' "$key" "$value" >> "$CONFIG_FILE"
  fi
}

set_flag "EnableLuaDebugLibrary" "1"
set_flag "LoggingEnabled" "1"
set_flag "MessageLog" "1"
chmod 444 "$CONFIG_FILE" 2>/dev/null || true

if [[ -d "$CACHE_DIR" ]]; then
  rm -rf "$CACHE_DIR"/*
fi

echo "✅ Debug Civ5 activé dans: $CONFIG_FILE"
echo "✅ Cache mods purgé: $CACHE_DIR"
echo "ℹ️  Si Civ5 réécrit config.ini, relancez ce script jeu fermé."
