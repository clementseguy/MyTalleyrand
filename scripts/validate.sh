#!/bin/bash
# Script de validation rapide du mod MyTalleyrand

echo "🔍 Validation du mod MyTalleyrand"
echo "=================================="
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Compteurs
PASSED=0
FAILED=0

# Test 1: Vérifier la présence des fichiers
echo "📁 Vérification de la structure..."
FILES=(
    "MyTalleyrand.modinfo"
    "README.md"
    ".gitignore"
    "XML/GameDefines.xml"
    "XML/Text.xml"
    "Lua/GameplayScript.lua"
    "SQL/ModSchema.sql"
    "docs/QUICKSTART.md"
    "docs/SUMMARY.md"
    "docs/DONE.md"
    "docs/GIT_COMMANDS.md"
    "docs/TESTING.md"
    "docs/VALIDATION.md"
    "docs/VALIDATION_REPORT.md"
    "docs/GITHUB_SETUP.md"
    "scripts/validate.sh"
    "scripts/start.sh"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "  ${GREEN}✓${NC} $file"
        ((PASSED++))
    else
        echo -e "  ${RED}✗${NC} $file manquant"
        ((FAILED++))
    fi
done
echo ""

# Test 2: Vérifier la syntaxe XML
echo "🔬 Validation de la syntaxe XML..."
if command -v xmllint &> /dev/null; then
    XML_FILES=(
        "MyTalleyrand.modinfo"
        "XML/GameDefines.xml"
        "XML/Text.xml"
    )
    
    for xml_file in "${XML_FILES[@]}"; do
        if xmllint --noout "$xml_file" 2>&1; then
            echo -e "  ${GREEN}✓${NC} $xml_file valide"
            ((PASSED++))
        else
            echo -e "  ${RED}✗${NC} $xml_file invalide"
            ((FAILED++))
        fi
    done
else
    echo -e "  ${YELLOW}⚠${NC}  xmllint non installé (installer avec: brew install libxml2)"
    echo "     Validation XML ignorée"
fi
echo ""

# Test 3: Vérifier la syntaxe Lua
echo "🔬 Validation de la syntaxe Lua..."
if command -v luac &> /dev/null; then
    if luac -p Lua/GameplayScript.lua 2>&1; then
        echo -e "  ${GREEN}✓${NC} GameplayScript.lua valide"
        ((PASSED++))
    else
        echo -e "  ${RED}✗${NC} GameplayScript.lua invalide"
        ((FAILED++))
    fi
else
    echo -e "  ${YELLOW}⚠${NC}  luac non installé (installer avec: brew install lua)"
    echo "     Validation Lua ignorée"
fi
echo ""

# Test 4: Vérifier la taille des fichiers
echo "📏 Vérification de la taille des fichiers (<500 lignes)..."
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        lines=$(wc -l < "$file")
        if [ "$lines" -lt 500 ]; then
            echo -e "  ${GREEN}✓${NC} $file: $lines lignes"
            ((PASSED++))
        else
            echo -e "  ${RED}✗${NC} $file: $lines lignes (>500)"
            ((FAILED++))
        fi
    fi
done
echo ""

# Test 5: Vérifier Git
echo "📦 Vérification de Git..."
if [ -d ".git" ]; then
    echo -e "  ${GREEN}✓${NC} Dépôt Git initialisé"
    ((PASSED++))
    
    # Vérifier les fichiers stagés
    staged=$(git diff --cached --name-only | wc -l)
    if [ "$staged" -gt 0 ]; then
        echo -e "  ${GREEN}✓${NC} $staged fichiers en staging"
        ((PASSED++))
    else
        echo -e "  ${YELLOW}⚠${NC}  Aucun fichier en staging"
    fi
else
    echo -e "  ${RED}✗${NC} Dépôt Git non initialisé"
    ((FAILED++))
fi
echo ""

# Résumé
echo "=================================="
echo "📊 Résumé de la validation"
echo "=================================="
echo -e "Tests réussis : ${GREEN}$PASSED${NC}"
if [ "$FAILED" -gt 0 ]; then
    echo -e "Tests échoués : ${RED}$FAILED${NC}"
else
    echo -e "Tests échoués : $FAILED"
fi
echo ""

if [ "$FAILED" -eq 0 ]; then
    echo -e "${GREEN}✅ Projet validé ! Prêt pour commit et GitHub${NC}"
    echo ""
    echo "Prochaines étapes:"
    echo "1. git commit -m \"feat: structure initiale du mod MyTalleyrand\""
    echo "2. Créer le dépôt sur GitHub (voir docs/GITHUB_SETUP.md)"
    echo "3. git remote add origin https://github.com/VOTRE_USERNAME/MyTalleyrand.git"
    echo "4. git push -u origin main"
else
    echo -e "${RED}❌ Des erreurs ont été détectées${NC}"
    echo "Consultez les messages ci-dessus pour plus de détails"
fi
