#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
INSTALL_BASE="${INSTALL_BASE:-$HOME/Applications/MyTalleyrandCoach}"
CIV5_DOCS_DIR="${CIV5_DOCS_DIR:-$HOME/Documents/Aspyr/Sid Meier's Civilization 5}"
MODS_DIR="$CIV5_DOCS_DIR/MODS"
MOD_TARGET_DIR="$MODS_DIR/MyTalleyrand"
EXPORT_DIR="$MOD_TARGET_DIR/export"
USER_CONFIG_DIR="$HOME/Library/Application Support/MyTalleyrand"
USER_CONFIG_FILE="$USER_CONFIG_DIR/coach.user.json"

COACH_API_KEY="${TALLEYRAND_OPENAI_API_KEY:-}"
COACH_SYSTEM_PROMPT="${TALLEYRAND_LLM_SYSTEM_PROMPT:-}"

printf "\n🚀 Installation MyTalleyrand (macOS)\n"
printf "===================================\n"

if [[ ! -d "$ROOT_DIR/mod" || ! -d "$ROOT_DIR/coach" ]]; then
  echo "❌ Ce script doit être lancé depuis le dépôt MyTalleyrand."
  exit 1
fi

mkdir -p "$MODS_DIR"
rm -rf "$MOD_TARGET_DIR"
mkdir -p "$MOD_TARGET_DIR"
cp -R "$ROOT_DIR/mod/." "$MOD_TARGET_DIR/"
mkdir -p "$EXPORT_DIR"
printf "✅ Mod installé dans: %s\n" "$MOD_TARGET_DIR"

mkdir -p "$INSTALL_BASE"
rm -rf "$INSTALL_BASE/coach"
cp -R "$ROOT_DIR/coach" "$INSTALL_BASE/coach"
printf "✅ Coach installé dans: %s\n" "$INSTALL_BASE/coach"

python3 -m venv "$INSTALL_BASE/coach/.venv"
"$INSTALL_BASE/coach/.venv/bin/pip" install --upgrade pip >/dev/null
"$INSTALL_BASE/coach/.venv/bin/pip" install -r "$INSTALL_BASE/coach/requirements.txt" >/dev/null
printf "✅ Environnement Python prêt\n"

mkdir -p "$USER_CONFIG_DIR"
if [[ ! -f "$USER_CONFIG_FILE" ]]; then
  cp "$ROOT_DIR/coach/config/coach.user.example.json" "$USER_CONFIG_FILE"
  printf "✅ Fichier de config utilisateur créé: %s\n" "$USER_CONFIG_FILE"
else
  printf "ℹ️  Fichier de config existant conservé: %s\n" "$USER_CONFIG_FILE"
fi

if [[ -z "$COACH_API_KEY" ]]; then
  read -r -p "Entrez votre clé OpenAI (laisser vide pour fallback local) : " COACH_API_KEY || true
fi
if [[ -n "$COACH_API_KEY" ]]; then
  /usr/bin/python3 - "$USER_CONFIG_FILE" "$COACH_API_KEY" <<'PY'
import json
import pathlib
import sys

cfg_path = pathlib.Path(sys.argv[1])
api_key = sys.argv[2]
data = json.loads(cfg_path.read_text(encoding="utf-8"))
data.setdefault("llm", {})["api_key"] = api_key
cfg_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY
  printf "✅ Clé API enregistrée dans %s\n" "$USER_CONFIG_FILE"
fi

if [[ -z "$COACH_SYSTEM_PROMPT" ]]; then
  read -r -p "Voulez-vous personnaliser le system prompt ? (o/N) " ANSWER || true
  if [[ "${ANSWER:-}" =~ ^[oOyY]$ ]]; then
    read -r -p "System prompt: " COACH_SYSTEM_PROMPT || true
  fi
fi

if [[ -n "$COACH_SYSTEM_PROMPT" ]]; then
  /usr/bin/python3 - "$USER_CONFIG_FILE" "$COACH_SYSTEM_PROMPT" <<'PY'
import json
import pathlib
import sys

cfg_path = pathlib.Path(sys.argv[1])
system_prompt = sys.argv[2]
data = json.loads(cfg_path.read_text(encoding="utf-8"))
data.setdefault("llm", {})["system_prompt"] = system_prompt
cfg_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY
  printf "✅ Prompt système mis à jour\n"
fi

cat <<EOF

🎯 Installation terminée.

Pour lancer le coach:
  cd "$INSTALL_BASE/coach"
  .venv/bin/python src/main.py

Le coach lit:
  - Settings par défaut: $INSTALL_BASE/coach/config/settings.json
  - Config utilisateur: $USER_CONFIG_FILE

EOF
