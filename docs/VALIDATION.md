# Checklist de validation avant commit

## Tests de base

### Structure du projet
- [ ] Tous les répertoires requis sont présents (XML/, Lua/, SQL/, Art/, docs/)
- [ ] Le fichier MyTalleyrand.modinfo est à la racine
- [ ] Le .gitignore est configuré
- [ ] Le README.md est complet et à jour
- [ ] Le docs/TESTING.md existe et est détaillé

### Validation de la syntaxe

#### Fichier .modinfo
```bash
# Vérifier la syntaxe XML
xmllint --noout MyTalleyrand.modinfo
# ou via un validateur en ligne
```
- [ ] Syntaxe XML valide
- [ ] UUID unique défini
- [ ] Version correcte (1.0)
- [ ] Tous les fichiers référencés existent

#### Fichiers XML
```bash
xmllint --noout XML/GameDefines.xml
xmllint --noout XML/Text.xml
```
- [ ] GameDefines.xml valide
- [ ] Text.xml valide
- [ ] Balises correctement fermées

#### Fichiers Lua
```bash
luac -p Lua/GameplayScript.lua
```
- [ ] Pas d'erreurs de syntaxe Lua
- [ ] Structure du code cohérente
- [ ] Commentaires présents

#### Fichiers SQL
- [ ] Syntaxe SQL correcte (vérification visuelle)
- [ ] Pas de requêtes dangereuses

### Architecture et qualité du code

- [ ] **Modularité** : Code organisé logiquement
- [ ] **Lisibilité** : Commentaires et nommage clairs
- [ ] **Taille des fichiers** : Tous < 500 lignes
  - MyTalleyrand.modinfo : ~70 lignes ✓
  - GameDefines.xml : ~5 lignes ✓
  - Text.xml : ~10 lignes ✓
  - GameplayScript.lua : ~15 lignes ✓
  - ModSchema.sql : ~7 lignes ✓
- [ ] **Pas de code mort** : Pas de code commenté inutile
- [ ] **Réutilisabilité** : Structure extensible

### Documentation

- [ ] README.md complet avec :
  - Description claire du mod
  - Instructions d'installation
  - Structure du projet
  - Guide de développement
  - Principes d'architecture
  - Checklist de contribution
  
- [ ] TESTING.md complet avec :
  - Tests de base
  - Tests fonctionnels
  - Tests de stabilité
  - Checklist avant commit
  - Guide de troubleshooting

### Test d'installation (si Civilization V disponible)

Si vous avez accès à Civilization V, effectuez les tests suivants :

1. **Installation du mod**
   ```bash
   # Copier le projet dans le dossier MODS de Civ5
   cp -r /Users/cseguy/workspace/MyTalleyrand ~/Documents/Aspyr/Sid\ Meier\'s\ Civilization\ 5/MODS/
   ```
   - [ ] Mod copié dans le bon répertoire

2. **Détection du mod**
   - [ ] Lancer Civilization V
   - [ ] Aller dans le menu MODS
   - [ ] Vérifier que MyTalleyrand apparaît

3. **Activation du mod**
   - [ ] Cocher MyTalleyrand
   - [ ] Cliquer sur Next
   - [ ] Pas de message d'erreur

4. **Test en jeu**
   - [ ] Démarrer une nouvelle partie
   - [ ] Vérifier que la partie démarre
   - [ ] Consulter les logs (pas d'erreur)

5. **Vérification des logs**
   ```bash
   # Afficher les logs
   cat ~/Documents/Aspyr/Sid\ Meier\'s\ Civilization\ 5/Logs/Database.log | grep -i error
   cat ~/Documents/Aspyr/Sid\ Meier\'s\ Civilization\ 5/Logs/Lua.log | grep -i error
   ```
   - [ ] Aucune erreur dans Database.log
   - [ ] Aucune erreur dans Lua.log

### Test sans Civilization V (validation minimale)

Si vous n'avez pas accès à Civilization V :

```bash
cd /Users/cseguy/workspace/MyTalleyrand

# Vérifier la structure
tree -L 2

# Vérifier les fichiers XML (si xmllint installé)
# brew install libxml2
xmllint --noout MyTalleyrand.modinfo 2>&1
xmllint --noout XML/GameDefines.xml 2>&1
xmllint --noout XML/Text.xml 2>&1

# Vérifier les fichiers Lua (si lua installé)
# brew install lua
luac -p Lua/GameplayScript.lua 2>&1

# Vérifier que tous les fichiers existent
test -f MyTalleyrand.modinfo && echo "✓ .modinfo OK"
test -f README.md && echo "✓ README OK"
test -f docs/TESTING.md && echo "✓ TESTING OK"
test -f .gitignore && echo "✓ .gitignore OK"
test -f XML/GameDefines.xml && echo "✓ GameDefines.xml OK"
test -f XML/Text.xml && echo "✓ Text.xml OK"
test -f Lua/GameplayScript.lua && echo "✓ GameplayScript.lua OK"
test -f SQL/ModSchema.sql && echo "✓ ModSchema.sql OK"
```

- [ ] Tous les fichiers existent
- [ ] Pas d'erreurs de syntaxe XML
- [ ] Pas d'erreurs de syntaxe Lua

### Git et GitHub

- [ ] Dépôt Git initialisé
- [ ] .gitignore configuré
- [ ] Tous les fichiers ajoutés au staging
- [ ] Pas de fichiers indésirables (logs, caches)

**Avant le commit :**
```bash
# Vérifier le statut
git status

# Vérifier les fichiers ajoutés
git diff --cached --name-only
```

### Checklist finale avant commit

- [ ] ✅ Pas de régression fonctionnelle (projet neuf)
- [ ] ✅ Architecture modulaire et lisible
- [ ] ✅ Code réutilisable et extensible
- [ ] ✅ Pas de code mort
- [ ] ✅ Fichiers < 500 lignes
- [ ] ✅ Documentation complète et à jour
- [ ] ✅ Instructions de test fournies
- [ ] ✅ .gitignore configuré

## Commit et GitHub

Une fois toutes les cases cochées :

```bash
# Commit initial
git commit -m "feat: structure initiale du mod MyTalleyrand

- Configuration .modinfo avec métadonnées
- Structure XML/Lua/SQL modulaire
- Documentation README et TESTING complète
- Gitignore configuré
- Architecture extensible < 500 lignes/fichier"

# Créer le dépôt sur GitHub (via interface web ou CLI)
# Puis :
git remote add origin https://github.com/VOTRE_USERNAME/MyTalleyrand.git
git branch -M main
git push -u origin main
```

## Résultat attendu

✅ Projet structuré et documenté
✅ Code de qualité prêt pour développement
✅ Documentation complète pour les contributeurs
✅ Tests définis pour garantir la stabilité
✅ Dépôt Git initialisé et prêt pour GitHub
