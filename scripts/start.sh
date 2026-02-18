#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "🎮 MyTalleyrand - démarrage rapide"
echo "================================="

echo "1) Validation projet"
./scripts/validate.sh || true

echo ""
echo "2) Smoke test coach (premier lancement local)"
./coach/scripts/first_test.sh

echo ""
echo "3) Prochaine étape mod Civ5"
echo "- Copier le contenu de mod/ dans votre dossier MODS Civ5"
echo "- Suivre mod/README.md pour le test en jeu"
