#!/bin/bash
# Script de démarrage rapide pour MyTalleyrand

echo "🎮 MyTalleyrand - Mod pour Civilization V"
echo "=========================================="
echo ""
echo "Bienvenue ! Ce script vous guide pour les prochaines étapes."
echo ""

# Vérifier l'état du projet
if [ ! -d ".git" ]; then
    echo "❌ Erreur: Dépôt Git non trouvé"
    exit 1
fi

# Compter les commits
COMMITS=$(git rev-list --all --count 2>/dev/null || echo 0)

if [ "$COMMITS" -eq 0 ]; then
    echo "📝 STATUT: Projet non commité (premier commit en attente)"
    echo ""
    echo "📋 PROCHAINES ÉTAPES:"
    echo ""
    echo "1️⃣  Valider le projet"
    echo "   → ./scripts/validate.sh"
    echo ""
    echo "2️⃣  Lire la documentation"
    echo "   → cat docs/SUMMARY.md"
    echo "   → cat docs/BACKLOG.md"
    echo ""
    echo "3️⃣  Tester l'application coach"
    echo "   → cd coach && python3 src/main.py"
    echo ""
    echo "4️⃣  Pousser les changements sur GitHub"
    echo "   → git add -A && git commit -m \"refactor: réorganisation repo mod + coach\""
    echo "   → git push"
    echo ""
    echo "📚 DOCUMENTATION DISPONIBLE:"
    echo "   - README.md : Vue d'ensemble du projet"
    echo "   - mod/README.md : Documentation du mod Civ5"
    echo "   - coach/README.md : Documentation de l'app coach"
    echo "   - docs/MACOS_GUIDE.md : Guide technique macOS complet"
    echo "   - docs/BACKLOG.md : User Stories et roadmap"
    echo "   - docs/TODO.md : Analyse de faisabilité"
    echo ""
    echo "🧪 TESTS:"
    echo "   - ./scripts/validate.sh : Validation automatique"
    echo ""
    
    # Proposer de lancer la validation
    echo "Voulez-vous lancer la validation maintenant ? (o/N)"
    read -r response
    if [[ "$response" =~ ^[Oo]$ ]]; then
        echo ""
        cd "$(dirname "$0")/.."
        ./scripts/validate.sh
    fi
    
else
    echo "✅ STATUT: Projet commité ($COMMITS commit(s))"
    echo ""
    
    # Vérifier si le remote existe
    if git remote | grep -q "origin"; then
        REMOTE_URL=$(git remote get-url origin 2>/dev/null)
        echo "📡 Remote configuré: $REMOTE_URL"
        echo ""
        
        # Vérifier si on peut contacter le remote
        if git ls-remote origin &>/dev/null; then
            echo "✅ Dépôt GitHub accessible"
            echo ""
            echo "🎉 Le projet est en ligne !"
            echo ""
            echo "📋 PROCHAINES ÉTAPES:"
            echo ""
            echo "1️⃣  Tester le mod dans Civilization V"
            echo "   → Voir docs/TESTING.md"
            echo ""
            echo "2️⃣  Installer les dépendances du coach"
            echo "   → cd coach && pip3 install -r requirements.txt"
            echo ""
            echo "2️⃣  Tester le mod dans Civilization V"
            echo "   → Copier mod/ vers ~/Documents/Aspyr/.../MODS/"
            echo "   → Voir mod/README.md"
            echo ""
            echo "3️⃣  Commencer le développement (US-001)"
            echo "   → Voir docs/BACKLOG.md"
            echo "   → Implémenter la collecte d'état de jeu
            echo "   → Vérifiez votre connexion et vos credentials"
            echo "   → git push -u origin main"
        fi
    else
        echo "📡 Pas de remote configuré"
        echo ""
        echo "📋 PROCHAINES ÉTAPES:"
        echo ""
        echo "1️⃣  Créer le dépôt GitHub"
        echo "   → Voir docs/GITHUB_SETUP.md ou docs/GIT_COMMANDS.md"
        echo ""
        echo "2️⃣  Ajouter le remote et pousser"
        echo "   → git remote add origin https://github.com/USERNAME/MyTalleyrand.git"
        echo "   → git push -u origin main"
    fi
fi

echo ""
echo "💡 AIDE:"
echo "   - Consulter docs/DONE.md pour le récapitulatif complet"
echo "   - Consulter docs/GIT_COMMANDS.md pour toutes les commandes"
echo "   - Lancer ./scripts/validate.sh pour valider le projet"
echo ""
