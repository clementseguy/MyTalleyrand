#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
INSTALL_BASE="${INSTALL_BASE:-$HOME/Applications/MyTalleyrandCoach}"
# Dossier de données/installation Civilization V.
# - Laissé vide : l'installateur le détecte automatiquement (Aspyr Store ou Steam).
# - Défini via la variable d'environnement CIV5_DOCS_DIR : force ce chemin (il est
#   tout de même validé avant utilisation).
# MODS_DIR / MOD_TARGET_DIR / EXPORT_DIR sont dérivés APRÈS détection (voir plus bas).
CIV5_DOCS_DIR="${CIV5_DOCS_DIR:-}"
USER_CONFIG_DIR="$HOME/Library/Application Support/MyTalleyrand"
USER_CONFIG_FILE="$USER_CONFIG_DIR/coach.user.json"

COACH_PROVIDER="${TALLEYRAND_LLM_PROVIDER:-mistral}"
MISTRAL_API_KEY="${TALLEYRAND_MISTRAL_API_KEY:-}"
OPENAI_API_KEY="${TALLEYRAND_OPENAI_API_KEY:-}"
COACH_API_KEY=""
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

# --- Détection du dossier Civilization V -----------------------------------

# Vrai si le dossier ressemble à des données utilisateur ou à une installation Civ5.
is_valid_civ5_dir() {
  local dir="$1"
  [[ -n "$dir" && -d "$dir" ]] || return 1
  # Dossier de données utilisateur (Aspyr/Steam) : contient (ou contiendra) MODS.
  local sub
  for sub in MODS Logs Saves cache ModUserData; do
    [[ -d "$dir/$sub" ]] && return 0
  done
  # Dossier d'installation Steam : marqueur Steam ou app du jeu.
  [[ -f "$dir/steam_appid.txt" ]] && return 0
  if compgen -G "$dir/*.app" >/dev/null 2>&1; then
    return 0
  fi
  return 1
}

# Liste, un chemin par ligne, les dossiers candidats à tester (données puis Steam).
civ5_candidate_dirs() {
  # Données utilisateur Aspyr Store (emplacement historique des MODS).
  printf '%s\n' "$HOME/Documents/Aspyr/Sid Meier's Civilization 5"
  # Données utilisateur Steam macOS (emplacement des MODS pour la version Steam).
  printf '%s\n' "$HOME/Library/Application Support/Sid Meier's Civilization 5"
  # Installation Steam par défaut (steamapps/common).
  local steam_root="$HOME/Library/Application Support/Steam"
  printf '%s\n' "$steam_root/steamapps/common/Sid Meier's Civilization V"
  # Bibliothèques Steam additionnelles déclarées dans libraryfolders.vdf.
  local vdf="$steam_root/config/libraryfolders.vdf"
  if [[ -f "$vdf" ]]; then
    local lib
    while IFS= read -r lib; do
      [[ -n "$lib" ]] || continue
      printf '%s\n' "$lib/steamapps/common/Sid Meier's Civilization V"
    done < <(sed -nE 's/^[[:space:]]*"path"[[:space:]]+"(.*)"[[:space:]]*$/\1/p' "$vdf")
  fi
}

# Renvoie (sur stdout) le premier dossier candidat valide, ou code retour 1.
detect_civ5_dir() {
  local dir
  while IFS= read -r dir; do
    if is_valid_civ5_dir "$dir"; then
      printf '%s\n' "$dir"
      return 0
    fi
  done < <(civ5_candidate_dirs)
  return 1
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

# --- Détection du dossier Civilization V -----------------------------------
printf "🔎 Recherche du dossier Civilization V (Aspyr et Steam)...\n"

# 1) Chemin imposé explicitement via variable d'environnement : on le valide.
if [[ -n "$CIV5_DOCS_DIR" ]]; then
  if is_valid_civ5_dir "$CIV5_DOCS_DIR"; then
    printf "   ✅ Dossier fourni via CIV5_DOCS_DIR: %s\n" "$CIV5_DOCS_DIR"
  else
    printf "   ⚠️  CIV5_DOCS_DIR ne pointe pas vers un dossier Civ5 valide: %s\n" "$CIV5_DOCS_DIR"
    CIV5_DOCS_DIR=""
  fi
fi

# 2) Détection automatique (Aspyr, données Steam, steamapps/common multi-bibliothèques).
if [[ -z "$CIV5_DOCS_DIR" ]]; then
  if CIV5_DOCS_DIR="$(detect_civ5_dir)"; then
    printf "   ✅ Dossier Civilization V détecté automatiquement:\n       %s\n" "$CIV5_DOCS_DIR"
  else
    CIV5_DOCS_DIR=""
  fi
fi

# 3) Saisie manuelle si rien n'a été trouvé, avec validation stricte.
if [[ -z "$CIV5_DOCS_DIR" ]]; then
  printf "   ⚠️  Aucun dossier Civilization V détecté automatiquement.\n"
  printf "       Le jeu doit avoir été installé (Aspyr Store ou Steam) et lancé au moins une fois.\n"
  if [[ "$INTERACTIVE" == "1" ]]; then
    printf "\n   Saisissez manuellement le chemin du dossier Civilization V.\n"
    printf "   Astuce : glissez-déposez le dossier depuis le Finder dans le Terminal.\n"
    printf "   Exemples de chemins :\n"
    printf "     • Aspyr : ~/Documents/Aspyr/Sid Meier's Civilization 5\n"
    printf "     • Steam : ~/Library/Application Support/Steam/steamapps/common/Sid Meier's Civilization V\n\n"
    while true; do
      read -r -p "   Chemin du dossier Civ5 (laisser vide pour annuler) : " MANUAL_DIR || true
      # Nettoie une saisie issue d'un glisser-déposer ou d'un copier-coller :
      # supprime les guillemets englobants et déséchappe les espaces (\ -> espace).
      MANUAL_DIR="${MANUAL_DIR%\"}"; MANUAL_DIR="${MANUAL_DIR#\"}"
      MANUAL_DIR="${MANUAL_DIR%\'}"; MANUAL_DIR="${MANUAL_DIR#\'}"
      MANUAL_DIR="${MANUAL_DIR//\\ / }"
      # Développe un ~ initial en $HOME.
      MANUAL_DIR="${MANUAL_DIR/#\~/$HOME}"
      if [[ -z "$MANUAL_DIR" ]]; then
        echo "   Installation interrompue : aucun dossier Civilization V fourni."
        echo "   Installez/lancez Civ5, puis relancez : ./scripts/install_macos.sh"
        exit 1
      fi
      if is_valid_civ5_dir "$MANUAL_DIR"; then
        CIV5_DOCS_DIR="$MANUAL_DIR"
        printf "   ✅ Dossier Civilization V validé: %s\n" "$CIV5_DOCS_DIR"
        break
      fi
      printf "   ❌ Ce dossier n'existe pas ou ne ressemble pas à une installation Civ5.\n"
      printf "      Il doit contenir le jeu (ou un sous-dossier MODS/Logs/Saves). Réessayez.\n\n"
    done
  else
    echo "   Installation interrompue : dossier Civilization V introuvable (mode non interactif)."
    echo "   Définissez CIV5_DOCS_DIR=/chemin/vers/Civ5 puis relancez."
    exit 1
  fi
fi

# Dérive les chemins du mod à partir du dossier Civ5 confirmé (auto-détecté ou saisi).
#
# Sur macOS, Civilization V peut créer plusieurs dossiers qui ressemblent à des
# dossiers utilisateur selon la distribution (Aspyr/Steam) et l'âge de
# l'installation. Certains Steam récents détectent le jeu dans
# ~/Library/Application Support/Sid Meier's Civilization 5, mais le menu Mods lit
# encore les mods depuis ~/Documents/Aspyr/Sid Meier's Civilization 5/MODS.
# Pour éviter une installation "réussie" mais invisible en jeu, on installe dans
# le dossier détecté ET dans le dossier Aspyr historique lorsqu'il est distinct.
MODS_DIR="$CIV5_DOCS_DIR/MODS"
MOD_TARGET_DIR="$MODS_DIR/MyTalleyrand"
EXPORT_DIR="$MOD_TARGET_DIR/export"
ASPYR_CIV5_DOCS_DIR="$HOME/Documents/Aspyr/Sid Meier's Civilization 5"
printf "\n"

mod_install_targets() {
  printf '%s\n' "$MOD_TARGET_DIR"
  if [[ "$CIV5_DOCS_DIR" != "$ASPYR_CIV5_DOCS_DIR" ]]; then
    printf '%s\n' "$ASPYR_CIV5_DOCS_DIR/MODS/MyTalleyrand"
  fi
}

while IFS= read -r target_dir; do
  [[ -n "$target_dir" ]] || continue
  mkdir -p "$(dirname "$target_dir")"
  rm -rf "$target_dir"
  mkdir -p "$target_dir"
  cp -R "$ROOT_DIR/mod/." "$target_dir/"
  mkdir -p "$target_dir/export"
  if [[ "$target_dir" == "$MOD_TARGET_DIR" ]]; then
    printf "✅ Mod installé dans: %s\n" "$target_dir"
  else
    printf "✅ Copie de compatibilité Steam/Aspyr installée dans: %s\n" "$target_dir"
  fi
done < <(mod_install_targets)

mkdir -p "$INSTALL_BASE"
rm -rf "$INSTALL_BASE/coach"
cp -R "$ROOT_DIR/coach" "$INSTALL_BASE/coach"
# Supprime le .venv copié accidentellement du workspace (qui ne doit pas être distribué)
rm -rf "$INSTALL_BASE/coach/.venv"
printf "✅ Coach installé dans: %s\n" "$INSTALL_BASE/coach"

VENV_DIR="$INSTALL_BASE/coach/.venv"
VENV_PY="$VENV_DIR/bin/python"
printf "🐍 Création de l'environnement Python (.venv)...\n"
if ! python3 -m venv "$VENV_DIR"; then
  echo "❌ Échec de la création de l'environnement virtuel Python (.venv)."
  echo "   Vérifiez que Python 3 est bien installé et complet (module venv) :"
  echo "        python3 -m venv --help"
  echo "   Si nécessaire, (ré)installez les outils Apple :"
  echo "        xcode-select --install"
  exit 1
fi
if [[ ! -x "$VENV_PY" ]]; then
  echo "❌ L'environnement virtuel a été demandé mais l'interpréteur est introuvable :"
  echo "        $VENV_PY"
  echo "   Échec de la création de l'environnement virtuel : vérifiez que Python 3"
  echo "   est bien installé et accessible (modules venv + ensurepip)."
  exit 1
fi
"$VENV_PY" -m pip install --upgrade pip >/dev/null
"$VENV_PY" -m pip install -r "$INSTALL_BASE/coach/requirements.txt" >/dev/null
printf "✅ Environnement Python prêt (%s)\n" "$VENV_DIR"

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

if [[ "$COACH_PROVIDER" != "mistral" && "$COACH_PROVIDER" != "openai" ]]; then
  printf "⚠️  Provider LLM invalide (%s), retour à mistral.\n" "$COACH_PROVIDER"
  COACH_PROVIDER="mistral"
fi
if [[ -z "${TALLEYRAND_LLM_PROVIDER:-}" && -n "$OPENAI_API_KEY" && -z "$MISTRAL_API_KEY" ]]; then
  COACH_PROVIDER="openai"
fi

if [[ "$INTERACTIVE" == "1" && -z "${TALLEYRAND_LLM_PROVIDER:-}" && -z "$MISTRAL_API_KEY" && -z "$OPENAI_API_KEY" ]]; then
  printf "\nProvider LLM à utiliser par défaut :\n"
  printf "  1. Mistral (recommandé)\n"
  printf "  2. OpenAI\n"
  read -r -p "Choix (Entrée = Mistral) : " PROVIDER_CHOICE || true
  if [[ "${PROVIDER_CHOICE:-}" == "2" || "${PROVIDER_CHOICE:-}" =~ ^[oO] ]]; then
    COACH_PROVIDER="openai"
  else
    COACH_PROVIDER="mistral"
  fi
fi

"$VENV_PY" - "$USER_CONFIG_FILE" "$COACH_PROVIDER" <<'PY'
import json
import pathlib
import sys

cfg_path = pathlib.Path(sys.argv[1])
provider = sys.argv[2]
data = json.loads(cfg_path.read_text(encoding="utf-8"))
data.setdefault("llm", {})["provider"] = provider
cfg_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY
printf "✅ Provider LLM configuré: %s\n" "$COACH_PROVIDER"

if [[ "$COACH_PROVIDER" == "mistral" ]]; then
  COACH_API_KEY="$MISTRAL_API_KEY"
else
  COACH_API_KEY="$OPENAI_API_KEY"
fi

if [[ -z "$COACH_API_KEY" ]]; then
  printf "\n────────────────────────────────────────────────────────\n"
  printf "🔑 Configuration de la clé %s (pour des conseils IA)\n" "$COACH_PROVIDER"
  printf "────────────────────────────────────────────────────────\n"
  printf "La clé permet au coach d'utiliser l'IA distante (%s).\n" "$COACH_PROVIDER"
  printf "  • L'obtenir est gratuit ; l'usage est payant (quelques centimes/partie).\n"
  printf "  • Sans clé, le coach fonctionne en mode local simplifié (sans IA).\n\n"

  if [[ "$INTERACTIVE" == "1" ]]; then
    read -r -p "Avez-vous déjà une clé $COACH_PROVIDER ? (o/N) " HAS_KEY || true
    if [[ ! "${HAS_KEY:-}" =~ ^[oOyY]$ ]]; then
      printf "\nPas de souci, créez-en une depuis la console du provider :\n"
      if [[ "$COACH_PROVIDER" == "mistral" ]]; then
        printf "  • https://console.mistral.ai/api-keys\n\n"
        KEY_URL="https://console.mistral.ai/api-keys"
      else
        printf "  1. Créez/connectez un compte : https://platform.openai.com/signup\n"
        printf "  2. Ajoutez un petit crédit : https://platform.openai.com/settings/organization/billing/overview\n"
        printf "  3. Générez la clé : https://platform.openai.com/api-keys → \"Create new secret key\"\n"
        printf "  4. Copiez la clé (elle ne s'affiche qu'une fois !)\n\n"
        KEY_URL="https://platform.openai.com/api-keys"
      fi
      read -r -p "Ouvrir la page de création de clé dans le navigateur ? (O/n) " OPEN_URL || true
      if [[ ! "${OPEN_URL:-}" =~ ^[nN]$ ]]; then
        open "$KEY_URL" 2>/dev/null || true
        printf "→ Page ouverte. Créez la clé, copiez-la, puis revenez ici.\n"
      fi
      pause_step "Appuyez sur Entrée quand votre clé est copiée (ou pour passer)... "
    fi
    printf "\nCollez votre clé (Cmd+V) puis Entrée. Elle reste masquée à l'écran.\n"
    printf "Laissez vide et Entrée pour utiliser le mode local sans IA.\n"
    while true; do
      read -r -s -p "Clé $COACH_PROVIDER : " COACH_API_KEY || true
      printf "\n"
      if [[ -z "$COACH_API_KEY" ]]; then
        printf "ℹ️  Aucune clé saisie : mode local simplifié activé.\n"
        break
      elif [[ "$COACH_PROVIDER" == "mistral" || "$COACH_API_KEY" == sk-* ]]; then
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
  "$VENV_PY" - "$USER_CONFIG_FILE" <<'PY'
import json
import pathlib
import sys

cfg_path = pathlib.Path(sys.argv[1])
data = json.loads(cfg_path.read_text(encoding="utf-8"))
llm = data.setdefault("llm", {})
llm.pop("api_key", None)
cfg_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY
  printf "%s" "$COACH_API_KEY" | PYTHONPATH="$INSTALL_BASE/coach" "$VENV_PY" -m src.keychain set "$COACH_PROVIDER" --stdin
  printf "✅ Clé API enregistrée dans le Keychain macOS (service MyTalleyrand, compte %s)\n" "$COACH_PROVIDER"
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
   1. Redémarrez Civilization V si le jeu était déjà ouvert.
   2. Menu Mods → activez « MyTalleyrand »
   3. Passez le jeu en mode fenêtré (Options → Vidéo)
   4. Lancez une partie : les conseils s'affichent au fil des tours.

   Si le menu Mods indique encore « Aucun Mod installé », vérifiez ces dossiers :
     • $MOD_TARGET_DIR
     • $ASPYR_CIV5_DOCS_DIR/MODS/MyTalleyrand

🩺  EN CAS DE SOUCI, diagnostic guidé :
     cd "$INSTALL_BASE/coach"
     .venv/bin/python src/main.py --onboarding

📄  Vos réglages :
   - Config utilisateur : $USER_CONFIG_FILE
   - Provider LLM : $COACH_PROVIDER
   - Clé API : stockée dans le Trousseau (Keychain) macOS, compte $COACH_PROVIDER
   - Settings par défaut : $INSTALL_BASE/coach/config/settings.json

EOF

# Propose d'ouvrir le dossier d'installation dans le Finder pour l'utilisateur.
if [[ "$INTERACTIVE" == "1" ]]; then
  read -r -p "Ouvrir le dossier du coach dans le Finder maintenant ? (O/n) " OPEN_FINDER || true
  if [[ ! "${OPEN_FINDER:-}" =~ ^[nN]$ ]]; then
    open "$INSTALL_BASE" 2>/dev/null || true
  fi
fi
