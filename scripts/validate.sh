#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "🔍 Validation du projet MyTalleyrand"
echo "===================================="

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASSED=0
FAILED=0

FILES=(
  "README.md"
  "LICENSE"
  "mod/MyTalleyrand.modinfo"
  "mod/README.md"
  "mod/XML/GameDefines.xml"
  "mod/XML/Text.xml"
  "mod/Lua/GameplayScript.lua"
  "mod/SQL/ModSchema.sql"
  "script/install_macos.sh"
  "coach/README.md"
  "coach/config/coach.user.example.json"
  "coach/src/main.py"
  "coach/src/llm_client.py"
  "coach/src/coach.py"
  "coach/src/overlay.py"
  "docs/README.md"
  "docs/DEVELOPMENT_PLAN.md"
  "docs/TESTING.md"
)

echo "📁 Vérification des fichiers requis"
for file in "${FILES[@]}"; do
  if [[ -f "$file" ]]; then
    echo -e "  ${GREEN}✓${NC} $file"
    ((PASSED+=1))
  else
    echo -e "  ${RED}✗${NC} $file manquant"
    ((FAILED+=1))
  fi
done

echo ""
echo "🔬 Validation XML"
if command -v xmllint >/dev/null 2>&1; then
  XML_FILES=("mod/MyTalleyrand.modinfo" "mod/XML/GameDefines.xml" "mod/XML/Text.xml")
  for xml_file in "${XML_FILES[@]}"; do
    if xmllint --noout "$xml_file" >/dev/null 2>&1; then
      echo -e "  ${GREEN}✓${NC} $xml_file valide"
      ((PASSED+=1))
    else
      echo -e "  ${RED}✗${NC} $xml_file invalide"
      ((FAILED+=1))
    fi
  done
else
  echo -e "  ${YELLOW}⚠${NC} xmllint non installé, validation XML ignorée"
fi

echo ""
echo "🧪 Tests Python coach"
if (cd coach && python3 -m pytest >/dev/null); then
  echo -e "  ${GREEN}✓${NC} pytest coach"
  ((PASSED+=1))
else
  echo -e "  ${RED}✗${NC} pytest coach"
  ((FAILED+=1))
fi

echo ""
echo "===================================="
echo "✅ Réussis: $PASSED"
echo "❌ Échoués: $FAILED"

if [[ "$FAILED" -gt 0 ]]; then
  exit 1
fi
