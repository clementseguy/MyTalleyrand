# Instructions pour créer le dépôt GitHub

## Étape 1 : Commit initial

Le projet a été validé et est prêt pour le commit initial. Pour commiter :

```bash
cd /Users/cseguy/workspace/MyTalleyrand

git commit -m "feat: structure initiale du mod MyTalleyrand

- Configuration .modinfo avec métadonnées du mod
- Structure XML/Lua/SQL modulaire et extensible
- Documentation README complète (installation, développement)
- Guide de test détaillé (TESTING.md)
- Checklist de validation (VALIDATION.md + VALIDATION_REPORT.md)
- Gitignore configuré pour macOS et outils de développement
- Architecture < 500 lignes/fichier, lisible et réutilisable

Mod de conseiller diplomatique et stratégique pour Civilization V"
```

## Étape 2 : Créer le dépôt sur GitHub

### Option A : Via l'interface web GitHub

1. Allez sur https://github.com/new
2. Remplissez les informations :
   - **Repository name** : `MyTalleyrand`
   - **Description** : `Mod de conseiller Talleyrand pour Civilization V - Recommandations diplomatiques et stratégiques`
   - **Visibilité** : Public ou Private (selon préférence)
   - **Ne pas cocher** "Initialize this repository with:"
     - README (déjà existant)
     - .gitignore (déjà existant)
     - License (à ajouter plus tard si souhaité)
3. Cliquez sur "Create repository"
4. GitHub affichera les instructions pour pousser un dépôt existant

### Option B : Via GitHub CLI (si installé)

```bash
# Installer GitHub CLI si nécessaire
brew install gh

# Se connecter à GitHub
gh auth login

# Créer le dépôt
gh repo create MyTalleyrand --public --source=. --remote=origin --description="Mod de conseiller Talleyrand pour Civilization V"

# Pousser le code
git push -u origin main
```

## Étape 3 : Pousser le code (si Option A)

Après avoir créé le dépôt sur GitHub, exécutez :

```bash
# Remplacez VOTRE_USERNAME par votre nom d'utilisateur GitHub
git remote add origin https://github.com/VOTRE_USERNAME/MyTalleyrand.git

# Vérifier que le remote est correct
git remote -v

# Pousser le code
git branch -M main
git push -u origin main
```

## Étape 4 : Configurer le dépôt GitHub (optionnel)

### Ajouter des topics

Sur la page GitHub du projet, cliquez sur l'icône engrenage à côté de "About" et ajoutez :
- `civilization-5`
- `civ5-mod`
- `game-mod`
- `lua`
- `xml`
- `strategy-game`

### Ajouter une licence

Si vous souhaitez ajouter une licence :

```bash
# Exemple avec MIT License
curl -o LICENSE https://raw.githubusercontent.com/licenses/license-templates/master/templates/mit.txt

# Éditer LICENSE pour ajouter votre nom et l'année
# Puis :
git add LICENSE
git commit -m "docs: ajout de la licence MIT"
git push
```

### Configurer GitHub Pages (optionnel)

Pour publier la documentation :
1. Settings → Pages
2. Source : Deploy from a branch
3. Branch : main → /docs
4. Save

## Étape 5 : Vérifier

Après le push, vérifiez sur GitHub :
- [ ] Le code est visible
- [ ] Le README.md s'affiche correctement
- [ ] La structure des dossiers est correcte
- [ ] Les fichiers sont bien présents

## Étape 6 : Prochaines actions

Une fois le dépôt créé :

1. **Cloner ailleurs pour tester** :
   ```bash
   cd /tmp
   git clone https://github.com/VOTRE_USERNAME/MyTalleyrand.git
   cd MyTalleyrand
   ```

2. **Créer une branche de développement** :
   ```bash
   git checkout -b develop
   git push -u origin develop
   ```

3. **Protéger la branche main** :
   - Settings → Branches → Add rule
   - Branch name pattern : `main`
   - Require a pull request before merging

4. **Créer les premiers issues** :
   - Issue #1 : Implémenter le conseiller Talleyrand
   - Issue #2 : Créer l'interface UI
   - Issue #3 : Ajouter les portraits et assets

## Commandes de vérification

```bash
# Vérifier le statut avant commit
git status

# Vérifier les fichiers qui seront commités
git diff --cached --name-only

# Vérifier que le remote est configuré (après étape 3)
git remote -v

# Vérifier la branche actuelle
git branch -a

# Voir l'historique
git log --oneline
```

## En cas de problème

### Erreur "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/VOTRE_USERNAME/MyTalleyrand.git
```

### Erreur d'authentification
```bash
# Utiliser un personal access token pour HTTPS
# Ou configurer SSH
gh auth login
```

### Le push est rejeté
```bash
# Si le dépôt distant a des commits différents
git pull origin main --allow-unrelated-histories
# Résoudre les conflits si nécessaire
git push origin main
```

## Résultat attendu

✅ Dépôt GitHub créé et accessible
✅ Code poussé sur la branche main
✅ README visible sur la page du projet
✅ Historique Git propre avec 1 commit initial

**URL du projet** : `https://github.com/VOTRE_USERNAME/MyTalleyrand`
