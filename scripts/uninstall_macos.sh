#!/usr/bin/env bash
set -euo pipefail

INSTALL_BASE="${INSTALL_BASE:-$HOME/Applications/MyTalleyrandCoach}"
CIV5_DOCS_DIR="${CIV5_DOCS_DIR:-$HOME/Documents/Aspyr/Sid Meier's Civilization 5}"
ASPYR_CIV5_DOCS_DIR="$HOME/Documents/Aspyr/Sid Meier's Civilization 5"
STEAM_APP_SUPPORT_CIV5_DOCS_DIR="$HOME/Library/Application Support/Sid Meier's Civilization 5"
MOD_TARGET_DIR="$CIV5_DOCS_DIR/MODS/MyTalleyrand"
USER_CONFIG_DIR="$HOME/Library/Application Support/MyTalleyrand"
LOG_FILE="${TALLEYRAND_LOG_FILE:-$HOME/talleyrand.log}"
REMOVE_USER_DATA="${REMOVE_USER_DATA:-0}"
REMOVE_LOGS="${REMOVE_LOGS:-0}"

printf "\n🧹 Désinstallation MyTalleyrand (macOS)\n"
printf "======================================\n"

if [[ -d "$INSTALL_BASE" ]]; then
  rm -rf "$INSTALL_BASE"
  printf "✅ Coach supprimé: %s\n" "$INSTALL_BASE"
else
  printf "ℹ️  Coach absent: %s\n" "$INSTALL_BASE"
fi

mod_uninstall_targets() {
  printf '%s\n' "$MOD_TARGET_DIR"
  printf '%s\n' "$ASPYR_CIV5_DOCS_DIR/MODS/MyTalleyrand"
  printf '%s\n' "$STEAM_APP_SUPPORT_CIV5_DOCS_DIR/MODS/MyTalleyrand"
}

while IFS= read -r target_dir; do
  [[ -n "$target_dir" ]] || continue
  if [[ -d "$target_dir" ]]; then
    rm -rf "$target_dir"
    printf "✅ Mod supprimé: %s\n" "$target_dir"
  else
    printf "ℹ️  Mod absent: %s\n" "$target_dir"
  fi
done < <(mod_uninstall_targets | awk '!seen[$0]++')

if command -v python3 >/dev/null 2>&1; then
  for provider in mistral openai; do
    if PYTHONPATH="$PWD/coach" python3 -m src.keychain delete "$provider" >/dev/null 2>&1; then
      printf "✅ Clé API %s supprimée du Keychain (service MyTalleyrand)\n" "$provider"
    else
      printf "ℹ️  Clé API %s absente ou suppression indisponible (keyring/macOS requis)\n" "$provider"
    fi
  done
else
  printf "⚠️  python3 introuvable: suppression Keychain ignorée\n"
fi

if [[ "$REMOVE_USER_DATA" == "1" ]]; then
  rm -rf "$USER_CONFIG_DIR"
  printf "✅ Configuration utilisateur supprimée: %s\n" "$USER_CONFIG_DIR"
else
  printf "ℹ️  Configuration utilisateur conservée: %s (REMOVE_USER_DATA=1 pour supprimer)\n" "$USER_CONFIG_DIR"
fi

if [[ "$REMOVE_LOGS" == "1" ]]; then
  rm -f "$LOG_FILE"
  printf "✅ Log supprimé: %s\n" "$LOG_FILE"
else
  printf "ℹ️  Log conservé: %s (REMOVE_LOGS=1 pour supprimer)\n" "$LOG_FILE"
fi

printf "\nDésinstallation terminée.\n"
