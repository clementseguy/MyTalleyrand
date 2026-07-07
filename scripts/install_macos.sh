#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
INSTALL_BASE="${INSTALL_BASE:-$HOME/Applications/MyTalleyrandCoach}"
CIV5_DOCS_DIR="${CIV5_DOCS_DIR:-}"
if [[ -z "$CIV5_DOCS_DIR" ]]; then
  CIV5_DOCS_DIR="$HOME/Documents/Aspyr/Sid Meier's Civilization 5"
fi
MODS_DIR="$CIV5_DOCS_DIR/MODS"
MOD_TARGET_DIR="$MODS_DIR/MyTalleyrand"
EXPORT_DIR="$MOD_TARGET_DIR/export"
USER_CONFIG_DIR="$HOME/Library/Application Support/MyTalleyrand"
USER_CONFIG_FILE="$USER_CONFIG_DIR/coach.user.json"

COACH_API_KEY="${TALLEYRAND_OPENAI_API_KEY:-}"
COACH_SYSTEM_PROMPT="${TALLEYRAND_LLM_SYSTEM_PROMPT:-}"

# Détecte si on tourne dans un vrai terminal interactif (pour les questions).
if [[ -t 0 ]]; then
  INTERACTIVE=1
else
  INTERACTIVE=0
fi

pause_step() {
  # Petite pause optionnelle pour laisser l'utilisateur lire avant de continuer.
  if [[ "$INTERACTIVE" == "1" ]]; then
    read -r -p "$1" _ || true
  fi
}

printf "\n🚀 Installation MyTalleyrand (macOS)\n"
printf "===================================\n"
printf "Ce programme installe le mod Civilization V et le coach.\n"
printf "Laissez-vous guider : il n'y a rien à coder. ✨\n\n"

if [[ ! -d "$ROOT_DIR/mod" || ! -d "$ROOT_DIR/coach" ]]; then
  echo "❌ Ce script doit être lancé depuis le dossier du projet MyTalleyrand."
  echo "   Astuce : dans le Terminal, tapez 'cd ' puis glissez-déposez le dossier"
  echo "   MyTalleyrand dans la fenêtre, appuyez sur Entrée, puis relancez :"
  echo "     ./scripts/install_macos.sh"
  exit 1
fi

# --- Vérification des prérequis --------------------------------------------
printf "🔎 Vérification des prérequis...\n"

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "❌ Cet installateur est prévu pour macOS uniquement."
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "❌ Python 3 n'est pas installé (nécessaire au coach)."
  echo ""
  echo "   👉 Solution la plus simple : installez les outils Apple en tapant :"
  echo "        xcode-select --install"
  echo "      Une fenêtre s'ouvre : cliquez sur « Installer », patientez,"
  echo "      puis relancez ./scripts/install_macos.sh"
  echo ""
  echo "   👉 Autre option : téléchargez Python depuis https://www.python.org/downloads/"
  exit 1
fi
printf "   ✅ Python 3 détecté (%s)\n" "$(python3 -V 2>&1)"

if [[ ! -d "$CIV5_DOCS_DIR" ]]; then
  printf "   ⚠️  Dossier Civilization V introuvable :\n       %s\n" "$CIV5_DOCS_DIR"
  printf "       Civ5 n'est peut-être pas installé ou n'a jamais été lancé.\n"
  printf "       (Lancez le jeu une fois pour créer ce dossier.)\n"
  if [[ "$INTERACTIVE" == "1" ]]; then
    read -r -p "   Continuer quand même l'installation ? (o/N) " CONT || true
    if [[ ! "${CONT:-}" =~ ^[oOyY]$ ]]; then
      echo "   Installation interrompue. Relancez après avoir installé/lancé Civ5."
      exit 1
    fi
  fi
else
  printf "   ✅ Dossier Civilization V trouvé\n"
fi
printf "\n"

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

cat > "$INSTALL_BASE/start_coach.command" <<EOF
#!/usr/bin/env bash
set -euo pipefail
cd "$INSTALL_BASE/coach"
exec .venv/bin/python src/main.py
EOF
chmod +x "$INSTALL_BASE/start_coach.command"
printf "✅ Lanceur double-cliquable créé: %s\n" "$INSTALL_BASE/start_coach.command"

mkdir -p "$USER_CONFIG_DIR"
if [[ ! -f "$USER_CONFIG_FILE" ]]; then
  cp "$ROOT_DIR/coach/config/coach.user.example.json" "$USER_CONFIG_FILE"
  printf "✅ Fichier de config utilisateur créé: %s\n" "$USER_CONFIG_FILE"
else
  printf "ℹ️  Fichier de config existant conservé: %s\n" "$USER_CONFIG_FILE"
fi

if [[ -z "$COACH_API_KEY" ]]; then
  printf "\n────────────────────────────────────────────────────────\n"
  printf "🔑 Configuration de la clé OpenAI (pour des conseils IA)\n"
  printf "────────────────────────────────────────────────────────\n"
  printf "La clé permet au coach d'utiliser l'IA d'OpenAI.\n"
  printf "  • L'obtenir est gratuit ; l'usage est payant (quelques centimes/partie).\n"
  printf "  • Sans clé, le coach fonctionne en mode local simplifié (sans IA).\n\n"

  if [[ "$INTERACTIVE" == "1" ]]; then
    read -r -p "Avez-vous déjà une clé OpenAI (commence par sk-...) ? (o/N) " HAS_KEY || true
    if [[ ! "${HAS_KEY:-}" =~ ^[oOyY]$ ]]; then
      printf "\nPas de souci, créons-en une :\n"
      printf "  1. Créez/connectez un compte : https://platform.openai.com/signup\n"
      printf "  2. Ajoutez un petit crédit : https://platform.openai.com/settings/organization/billing/overview\n"
      printf "  3. Générez la clé : https://platform.openai.com/api-keys → \"Create new secret key\"\n"
      printf "  4. Copiez la clé (elle ne s'affiche qu'une fois !)\n\n"
      read -r -p "Ouvrir la page de création de clé dans le navigateur ? (O/n) " OPEN_URL || true
      if [[ ! "${OPEN_URL:-}" =~ ^[nN]$ ]]; then
        open "https://platform.openai.com/api-keys" 2>/dev/null || true
        printf "→ Page ouverte. Créez la clé, copiez-la, puis revenez ici.\n"
      fi
      pause_step "Appuyez sur Entrée quand votre clé est copiée (ou pour passer)... "
    fi
    printf "\nCollez votre clé (Cmd+V) puis Entrée. Elle reste masquée à l'écran.\n"
    printf "Laissez vide et Entrée pour utiliser le mode local sans IA.\n"
    while true; do
      read -r -s -p "Clé OpenAI : " COACH_API_KEY || true
      printf "\n"
      if [[ -z "$COACH_API_KEY" ]]; then
        printf "ℹ️  Aucune clé saisie : mode local simplifié activé.\n"
        break
      elif [[ "$COACH_API_KEY" == sk-* ]]; then
        break
      else
        printf "⚠️  Une clé OpenAI commence normalement par \"sk-\".\n"
        read -r -p "   Réessayer la saisie ? (O/n) " RETRY || true
        if [[ "${RETRY:-}" =~ ^[nN]$ ]]; then
          break
        fi
        COACH_API_KEY=""
      fi
    done
  fi
fi
if [[ -n "$COACH_API_KEY" ]]; then
  "$INSTALL_BASE/coach/.venv/bin/python" - "$USER_CONFIG_FILE" <<'PY'
import json
import pathlib
import sys

cfg_path = pathlib.Path(sys.argv[1])
data = json.loads(cfg_path.read_text(encoding="utf-8"))
llm = data.setdefault("llm", {})
llm.pop("api_key", None)
cfg_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY
  printf "%s" "$COACH_API_KEY" | PYTHONPATH="$INSTALL_BASE/coach" "$INSTALL_BASE/coach/.venv/bin/python" -m src.keychain set openai --stdin
  printf "✅ Clé API enregistrée dans le Keychain macOS (service MyTalleyrand, compte openai)\n"
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

🎯 Installation terminée !

▶️  POUR LANCER LE COACH :
   Double-cliquez sur « start_coach.command » dans le Finder :
     Applications → MyTalleyrandCoach → start_coach.command
   (Ou depuis le Terminal : open "$INSTALL_BASE/start_coach.command")

   ⚠️  La 1ʳᵉ fois, si macOS bloque le lanceur :
       clic droit sur start_coach.command → Ouvrir → Ouvrir.

🎮  DANS CIVILIZATION V :
   1. Menu Mods → activez « MyTalleyrand »
   2. Passez le jeu en mode fenêtré (Options → Vidéo)
   3. Lancez une partie : les conseils s'affichent au fil des tours.

🩺  EN CAS DE SOUCI, diagnostic guidé :
     cd "$INSTALL_BASE/coach"
     .venv/bin/python src/main.py --onboarding

📄  Vos réglages :
   - Config utilisateur : $USER_CONFIG_FILE
   - Clé OpenAI : stockée dans le Trousseau (Keychain) macOS
   - Settings par défaut : $INSTALL_BASE/coach/config/settings.json

EOF

# Propose d'ouvrir le dossier d'installation dans le Finder pour l'utilisateur.
if [[ "$INTERACTIVE" == "1" ]]; then
  read -r -p "Ouvrir le dossier du coach dans le Finder maintenant ? (O/n) " OPEN_FINDER || true
  if [[ ! "${OPEN_FINDER:-}" =~ ^[nN]$ ]]; then
    open "$INSTALL_BASE" 2>/dev/null || true
  fi
fi
