# MyTalleyrand - Coach LLM pour Civilization V

**Mod Civilization V + Application coach utilisant un LLM pour vous guider en temps réel**

## 🎯 Description

MyT⚡ Démarrage rapide

### 1. Cloner le repository

```bash
git clone https://github.com/clementseguy/MyTalleyrand.git
cd MyTalleyrand
```

### 2. Installer le mod Civilization V

Voir [mod/README.md](mod/README.md) pour les instructions détaillées.

**macOS (Aspyr) :**
```bash
cp -r mod/ ~/Documents/Aspyr/Sid\ Meier\'s\ Civilization\ 5/MODS/MyTalleyrand/
mkdir -p ~/Documents/Aspyr/Sid\ Meier\'s\ Civilization\ 5/MODS/MyTalleyrand/export/
```

### 3. Installer l'application coach

Voir [coach/README.md](coach/README.md) pour les instructions détaillées.

```bash
cd coach
pip3 install -r requirements.txt

# Configurer la clé API
python3 src/main.py --setup
```

### 4. Lancer le coach

```bash
cd coach
python3 src/main.py
```

### 5. Jouer !

1. Lancer Civilization V en **mode fenêtré**
2. Activer le mod **MyTalleyrand**
3. Démarrer une partie
4. L'overlay s'affiche avec les conseils du coachment.

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

###🛠️ Stack technique

### Mod Civilization V
- **Lua** : Export de l'état du jeu
- **XML** : Définitions et traductions
- **SQL** : Modifications de base de données

### Application Coach
- **Python 3.11+** : Langage principal
- **PyQt6** : Interface overlay
- **OpenAI API** : LLM (GPT-4o-mini recommandé)
- **Watchdog** : Surveillance fichiers
- **Keyring** : Stockage sécurisé clés API (Keychain macOS)

### Plateforme
- **macOS 13+** (Ventura, Sonoma) - prioritaire
- Windows et Linux en développement

## 📚 Documentation

- [**Guide technique macOS**](docs/MACOS_GUIDE.md) : Détails implémentation, permissions, overlay
- [**Backlog**](docs/BACKLOG.md) : 14 User Stories, roadmap 4 sprints
- [**Analyse faisabilité**](docs/TODO.md) : Choix techniques et contraintes
- [**README Mod**](mod/README.md) : Installation et utilisation du mod Civ5
- [**README Coach**](coach/README.md) : Installation et utilisation de l'app Python

## 🚧 Statut du projet

**Phase actuelle :** Phases 2, 3, 4 et 5 lancées (LLM + overlay MVP + logique coach + stabilisation)

### ✅ Complété
- Architecture hybride définie (Mod + App externe)
- Stack technique validée (Python + PyQt6 + OpenAI)
- Documentation complète (1900+ lignes)
- Backlog détaillé (14 User Stories, 115 points)
- Spécifications macOS documentées

### ✅ Travaux lancés (Phases 2-5)
- **Phase 2 / US-003** : client LLM structuré (JSON strict), retry/timeout et fallback local
- **Phase 3 / US-004** : overlay MVP avec position persistante et bascule affichage/masquage
- **Phase 4 / US-006-007-008** : logique de déclenchement (tour 1 puis tous les 10 tours), recommandations catégorisées et historique local
- **Phase 5 / US-014** : premiers tests d'intégration de bout en bout + validation automatisée de la chaîne watcher → coach → overlay

Voir [docs/DEVELOPMENT_PLAN.md](docs/DEVELOPMENT_PLAN.md) pour le séquencement détaillé.

## 💡 Fonctionnalités prévues

### MVP (Sprint 0-1)
- ✅🧪 Validation et tests

```bash
# Validation automatique de la structure
./scripts/validate.sh

# Guide interactif de démarrage
./scripts/start.sh

 # Tests unitaires Python
cd coach && python3 -m pytest tests/

# Premier test de lancement coach
./coach/scripts/first_test.sh
```

## 🤝 Contribution

Les contributions sont bienvenues ! Consultez [docs/BACKLOG.md](docs/BACKLOG.md) pour voir les User Stories disponibles.

### Workflow de développement
1. Fork le projet
2. Créer une branche (`git checkout -b feature/US-XXX`)
3. Implémenter la User Story
4. Tester (`./scripts/validate.sh`)
5. Commiter (`git commit -m "feat: US-XXX - description"`)
6. Push et Pull Request

## 🐛 Problèmes connus

- **Overlay macOS** : Nécessite Civ5 en mode fenêtré (plein écran non supporté)
- **Permissions** : Accès Accessibilité requis sur macOS
- **Performance** : Overlay optimisé pour < 5% CPU

Voir [docs/MACOS_GUIDE.md](docs/MACOS_GUIDE.md) section "Support" pour solutions.

## 📜 Licence

À définir

## 👤 Auteur

**Clément Séguy**
- GitHub: [@clementseguy](https://github.com/clementseguy)

## 🙏 Remerciements

- Communauté CivFanatics pour la documentation modding
- OpenAI pour l'API GPT
- PyQt6 pour le framework UI

---

**Version actuelle :** 0.3.0 (Phases 3-5 en cours)  
**Dernière mise à jour :** 22 décembre 2025