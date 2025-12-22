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
    echo "   → cat docs/VALIDATION_REPORT.md"
    echo ""
    echo "3️⃣  Commiter le projet"
    echo "   → Consulter docs/GIT_COMMANDS.md pour la commande exacte"
    echo "   → ou copier/coller depuis docs/GITHUB_SETUP.md"
    echo ""
    echo "4️⃣  Créer le dépôt GitHub"
    echo "   → Option A: gh repo create (voir docs/GIT_COMMANDS.md)"
    echo "   → Option B: Via l'interface web (voir docs/GITHUB_SETUP.md)"
    echo ""
    echo "5️⃣  Pousser sur GitHub"
    echo "   → git push -u origin main"
    echo ""
    echo "📚 DOCUMENTATION DISPONIBLE:"
    echo "   - README.md : Vue d'ensemble"
    echo "   - docs/SUMMARY.md : Récapitulatif complet"
    echo "   - docs/DONE.md : Mission accomplie !"
    echo "   - docs/GIT_COMMANDS.md : Commandes Git prêtes"
    echo "   - docs/TESTING.md : Guide de test"
    echo "   - docs/GITHUB_SETUP.md : Configuration GitHub"
    echo ""
    echo "🧪 TESTS:"
    echo "   - ./validate.sh : Validation automatique"
    echo ""
    
    # Proposer de lancer la validation
    echo "Voulez-vous lancer la validation maintenant ? (o/N)"
    read -r response
    if [[ "$response" =~ ^[Oo]$ ]]; then
        echo ""
        ./validate.sh
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
            echo "2️⃣  Créer une branche de développement"
            echo "   → git checkout -b develop"
            echo "   → git push -u origin develop"
            echo ""
            echo "3️⃣  Commencer le développement"
            echo "   → Implémenter le conseiller Talleyrand"
            echo "   → Voir README.md section \"Développement\""
            echo ""
        else
            echo "⚠️  Remote configuré mais inaccessible"
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
