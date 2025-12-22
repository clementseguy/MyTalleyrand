# Commandes Git - MyTalleyrand

Ce fichier contient toutes les commandes Git prêtes à copier/coller.

## ✅ État actuel

- Dépôt Git initialisé ✅
- 13 fichiers en staging ✅
- Validation complète effectuée ✅
- **Prêt pour commit initial**

## 📝 Commit initial

```bash
git commit -m "feat: structure initiale du mod MyTalleyrand

- Configuration .modinfo avec métadonnées du mod
- Structure XML/Lua/SQL modulaire et extensible
- Documentation README complète (installation, développement)
- Guide de test détaillé (TESTING.md)
- Checklist de validation (VALIDATION.md + VALIDATION_REPORT.md)
- Guide de configuration GitHub (GITHUB_SETUP.md)
- Script de validation automatique (validate.sh)
- Gitignore configuré pour macOS et outils de développement
- Architecture < 500 lignes/fichier, lisible et réutilisable

Mod de conseiller diplomatique et stratégique pour Civilization V"
```

## 🌐 Création du dépôt GitHub

### Option 1 : Via GitHub CLI (recommandé si installé)

```bash
# Installer GitHub CLI si nécessaire
brew install gh

# Se connecter
gh auth login

# Créer le dépôt et pousser
gh repo create MyTalleyrand \
  --public \
  --source=. \
  --remote=origin \
  --description="Mod de conseiller Talleyrand pour Civilization V - Recommandations diplomatiques et stratégiques"

# Pousser le code
git push -u origin main
```

### Option 2 : Via l'interface web GitHub

1. **Créer le dépôt sur GitHub** :
   - Aller sur https://github.com/new
   - Repository name: `MyTalleyrand`
   - Description: `Mod de conseiller Talleyrand pour Civilization V`
   - Public ou Private selon préférence
   - **Ne rien initialiser** (pas de README, ni .gitignore, ni LICENSE)
   - Cliquer "Create repository"

2. **Pousser le code** :
```bash
# Remplacer VOTRE_USERNAME par votre nom d'utilisateur GitHub
git remote add origin https://github.com/VOTRE_USERNAME/MyTalleyrand.git
git branch -M main
git push -u origin main
```

## 🔍 Vérifications après push

```bash
# Vérifier que le remote est configuré
git remote -v

# Vérifier la branche
git branch -a

# Voir l'historique
git log --oneline

# Vérifier le statut
git status
```

## 🎯 Configuration post-création

### Ajouter des topics sur GitHub
Via l'interface web, ajouter :
- `civilization-5`
- `civ5-mod`
- `game-mod`
- `lua`
- `xml`
- `strategy-game`
- `modding`

### Créer une branche de développement

```bash
git checkout -b develop
git push -u origin develop
```

### Protéger la branche main (via GitHub Settings)
- Settings → Branches → Add rule
- Branch name pattern: `main`
- Cocher "Require a pull request before merging"
- Cocher "Require approvals" (1)

### Ajouter une licence (optionnel)

```bash
# Exemple avec MIT License
curl -o LICENSE https://raw.githubusercontent.com/licenses/license-templates/master/templates/mit.txt

# Éditer LICENSE pour ajouter votre nom et l'année 2025
# Puis :
git add LICENSE
git commit -m "docs: ajout de la licence MIT"
git push
```

## 🚀 Workflow de développement futur

### Créer une nouvelle fonctionnalité

```bash
# Partir de develop
git checkout develop
git pull origin develop

# Créer une branche feature
git checkout -b feature/nom-de-la-fonctionnalite

# Développer, tester, commiter
git add .
git commit -m "feat: description de la fonctionnalité"

# Pousser la branche
git push -u origin feature/nom-de-la-fonctionnalite

# Créer une Pull Request sur GitHub
```

### Merge dans main

```bash
# Après validation de la PR
git checkout develop
git pull origin develop

git checkout main
git pull origin main
git merge develop
git push origin main

# Créer un tag de version
git tag -a v1.0.0 -m "Version 1.0.0 - Première version stable"
git push origin v1.0.0
```

## 🔧 Commandes utiles

### Voir les modifications non commitées
```bash
git diff
```

### Voir les fichiers modifiés
```bash
git status --short
```

### Annuler des modifications (avant commit)
```bash
# Annuler les modifications d'un fichier
git checkout -- nom_du_fichier

# Tout annuler
git reset --hard HEAD
```

### Modifier le dernier commit
```bash
# Ajouter des fichiers oubliés
git add fichier_oublie
git commit --amend --no-edit

# Modifier le message du dernier commit
git commit --amend -m "Nouveau message"
```

### Synchroniser avec GitHub
```bash
# Récupérer les changements
git pull origin main

# Pousser les changements
git push origin main
```

## 📋 Checklist avant chaque commit

- [ ] `./validate.sh` passe avec succès
- [ ] Documentation mise à jour si nécessaire
- [ ] Fichiers < 500 lignes
- [ ] Pas de code mort
- [ ] Tests effectués (voir docs/TESTING.md)
- [ ] Message de commit descriptif

## 🆘 En cas de problème

### Le remote existe déjà
```bash
git remote remove origin
git remote add origin https://github.com/VOTRE_USERNAME/MyTalleyrand.git
```

### Erreur d'authentification
```bash
gh auth login
# ou configurer un Personal Access Token
```

### Conflit lors du push
```bash
git pull origin main --rebase
# Résoudre les conflits
git add .
git rebase --continue
git push origin main
```

### Annuler le dernier commit (non poussé)
```bash
git reset --soft HEAD~1
```

### Annuler le dernier commit (déjà poussé)
```bash
git revert HEAD
git push origin main
```

## 📚 Ressources

- Documentation Git : https://git-scm.com/doc
- GitHub CLI : https://cli.github.com/
- Guide GitHub : https://docs.github.com/
- Civilization V Modding : https://civilization.fandom.com/wiki/Modding_(Civ5)

## ✅ Commande de validation rapide

```bash
# Valider le projet avant commit
./validate.sh
```

## 🎉 Prêt !

Toutes les commandes sont prêtes. Suivez les étapes dans l'ordre et consultez `docs/GITHUB_SETUP.md` pour plus de détails.
