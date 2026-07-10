#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "🎮 MyTalleyrand - démarrage rapide"
echo "================================="

echo "1) Installation macOS (mod + coach)"
echo "   ./scripts/install_macos.sh"

echo ""
echo "2) Validation projet"
./scripts/validate.sh || true

echo ""
echo "3) Lancer le coach du dépôt courant"
echo "   ./scripts/run_coach.sh --debug"

echo ""
echo "4) Lancer le coach installé"
echo "   open ~/Applications/MyTalleyrandCoach/start_coach.command"
