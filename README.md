# MyTalleyrand - Mod Conseiller pour Civilization V

## Description

MyTalleyrand est un mod pour Civilization V qui introduit un nouveau conseiller diplomatique et stratégique inspiré de Talleyrand, offrant des recommandations intelligentes pour vos décisions politiques et militaires.

## Prérequis

- Civilization V installé (avec ou sans extensions)
- Système d'exploitation : Windows, macOS ou Linux

## Installation

### Méthode 1 : Installation manuelle

1. Localisez votre dossier Mods de Civilization V :
   - **Windows** : `Documents\My Games\Sid Meier's Civilization 5\MODS\`
   - **macOS** : `~/Documents/Aspyr/Sid Meier's Civilization 5/MODS/`
   - **Linux** : `~/.local/share/Aspyr/Sid Meier's Civilization 5/MODS/`

2. Copiez le dossier `MyTalleyrand` dans le répertoire MODS

3. Lancez Civilization V et activez le mod depuis le menu "Mods"

### Méthode 2 : Via Steam Workshop (à venir)

Publication sur Steam Workshop prévue prochainement.

## Structure du projet

```
MyTalleyrand/
├── MyTalleyrand.modinfo    # Fichier de configuration du mod
├── XML/                     # Définitions de gameplay
│   ├── GameDefines.xml     # Nouvelles unités, bâtiments, etc.
│   └── Text.xml            # Textes et traductions
├── Lua/                     # Scripts de gameplay
│   └── GameplayScript.lua  # Logique principale du conseiller
├── SQL/                     # Modifications de base de données
│   └── ModSchema.sql       # Requêtes SQL
├── Art/                     # Assets graphiques (icônes, portraits)
├── scripts/                 # Scripts de validation et utilitaires
│   ├── validate.sh         # Script de validation automatique
│   └── start.sh            # Guide interactif de démarrage
└── docs/                    # Documentation complète
    ├── TESTING.md          # Guide de test
    ├── VALIDATION.md       # Checklist de validation
    ├── GITHUB_SETUP.md     # Configuration GitHub
    ├── GIT_COMMANDS.md     # Commandes Git
    ├── SUMMARY.md          # Récapitulatif du projet
    ├── DONE.md             # Mission accomplie
    └── QUICKSTART.md       # Démarrage rapide
```

## Architecture

Le mod suit une architecture modulaire :

- **XML** : Contient les définitions statiques (textes, éléments UI)
- **Lua** : Implémente la logique du conseiller et les événements de gameplay
- **SQL** : Modifie les données existantes si nécessaire
- **Art** : Stocke les ressources graphiques (portrait du conseiller, icônes)

### Principes de développement

- **Modularité** : Chaque composant est séparé et réutilisable
- **Lisibilité** : Code commenté et structuré
- **Limite de taille** : Fichiers < 500 lignes max
- **Tests** : Validation après chaque modification
- **Qualité** : Aucune régression fonctionnelle

## Développement

### Modifier le mod

1. **Ajouter des conseils** : Éditez `Lua/GameplayScript.lua`
2. **Ajouter des textes** : Éditez `XML/Text.xml`
3. **Modifier l'UI** : Éditez les fichiers Lua correspondants
4. **Modifier les données** : Éditez `SQL/ModSchema.sql`

### Tester les modifications

Consultez [docs/TESTING.md](docs/TESTING.md) pour les instructions détaillées de test.

**Test rapide après modification :**
1. Sauvegardez vos fichiers
2. Relancez Civilization V
3. Démarrez une nouvelle partie avec le mod activé
4. Vérifiez les logs dans `Logs/Database.log` et `Logs/Lua.log`
5. Testez les fonctionnalités du conseiller

### Vérifier la stabilité

1. **Syntaxe XML** : Validez avec un parseur XML
2. **Syntaxe Lua** : Vérifiez avec `luac -p fichier.lua`
3. **Logs du jeu** : Consultez les fichiers de log après chargement
4. **Test en jeu** : Lancez une partie complète (50+ tours)
5. **Sauvegarde/Chargement** : Testez la persistance des données

### Scripts utilitaires

Le projet inclut des scripts pour faciliter le développement :

```bash
# Validation automatique du projet
./scripts/validate.sh

# Guide interactif de démarrage
./scripts/start.sh
```

## Fonctionnalités prévues

- ✨ Conseiller Talleyrand avec interface dédiée
- 🎯 Recommandations diplomatiques contextuelles
- ⚔️ Conseils stratégiques militaires
- 🏛️ Analyse des relations internationales
- 📊 Évaluation des forces en présence

## Compatibilité

- ✅ Solo
- ✅ Multijoueur
- ✅ Hotseat
- ✅ Windows / macOS / Linux
- ⚠️ Affecte les sauvegardes (activez avant de commencer une partie)

## Contribution

Les contributions sont les bienvenues ! Respectez les règles suivantes :

1. **Pas de régression** : Toute modification doit être testée
2. **Code modulaire** : Réutilisez les composants existants
3. **Suppression du code mort** : Nettoyez le code inutilisé
4. **Documentation** : Mettez à jour le README et TESTING.md
5. **Tests avant commit** : Validez la stabilité complète

## Licence

À définir

## Auteur

Clément Séguy

## Historique des versions

### v1.0 (En développement)
- Structure initiale du projet
- Configuration de base du mod
- Documentation complète