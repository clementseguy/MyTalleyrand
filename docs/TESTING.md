# Guide de test - MyTalleyrand

## Objectif

Ce document décrit comment tester le mod MyTalleyrand après installation ou modification, afin de garantir sa stabilité et son bon fonctionnement.

## Prérequis

- Civilization V installé
- Mod MyTalleyrand copié dans le dossier MODS
- Accès aux fichiers de logs du jeu

## 0. Tests automatisés coach (Phases 3-5)

Depuis la mise en place des phases 3, 4 et 5, exécuter en priorité :

```bash
cd coach
python3 -m pytest tests/test_overlay.py tests/test_coach_engine.py tests/test_pipeline_integration.py tests/test_watcher.py tests/test_config.py tests/test_gamestate_schema.py
```

**Ce que ces tests couvrent**
- Overlay MVP : persistance position/visibilité + rendu des conseils.
- Logique coach : déclenchement tour 1 puis tous les 10 tours, historique local.
- Intégration : chaîne watcher → coach → overlay.

## 1. Tests de base (après installation)

### 1.1 Vérification de la détection du mod

**Objectif** : S'assurer que Civilization V détecte le mod

**Procédure** :
1. Lancez Civilization V
2. Cliquez sur "MODS" dans le menu principal
3. Vérifiez que "MyTalleyrand" apparaît dans la liste

**Résultat attendu** : Le mod est visible avec son nom, description et version

**En cas d'échec** : Vérifiez l'emplacement du fichier `.modinfo` et sa syntaxe XML

### 1.2 Activation du mod

**Objectif** : Activer le mod sans erreur

**Procédure** :
1. Dans le menu MODS, cochez "MyTalleyrand"
2. Cliquez sur "Next"
3. Observez les messages de chargement

**Résultat attendu** : Aucun message d'erreur, retour au menu principal

**En cas d'échec** : Consultez `Documents/My Games/Sid Meier's Civilization 5/Logs/Database.log`

### 1.3 Démarrage d'une partie

**Objectif** : Lancer une partie avec le mod actif

**Procédure** :
1. Cliquez sur "SINGLE PLAYER" puis "SETUP GAME"
2. Configurez une partie rapide (taille Duel, vitesse Quick)
3. Cliquez sur "START GAME"
4. Attendez le chargement complet

**Résultat attendu** : La partie démarre sans crash, écran de jeu s'affiche

**En cas d'échec** : Consultez `Logs/Lua.log` pour les erreurs de script

## 2. Tests fonctionnels (après modification du code)

### 2.1 Test des modifications XML

**Objectif** : Vérifier que les modifications XML sont chargées

**Procédure** :
1. Modifiez `XML/GameDefines.xml` ou `XML/Text.xml`
2. Sauvegardez le fichier
3. Relancez Civilization V
4. Chargez le mod (il sera rechargé automatiquement)
5. Démarrez une nouvelle partie

**Vérifications** :
- Consultez `Logs/Database.log` : recherchez "Loading MyTalleyrand"
- Vérifiez l'absence d'erreurs "ERROR" ou "WARNING"
- Testez en jeu les éléments modifiés

**En cas d'erreur** :
- Validez la syntaxe XML avec un outil en ligne ou éditeur XML
- Vérifiez que les références (types, clés) existent dans le jeu

### 2.2 Test des modifications Lua

**Objectif** : Vérifier que les scripts Lua fonctionnent

**Procédure** :
1. Modifiez `Lua/GameplayScript.lua`
2. Ajoutez des `print()` pour déboguer si nécessaire
3. Sauvegardez le fichier
4. Relancez Civilization V et le mod
5. Démarrez une nouvelle partie

**Vérifications** :
- Consultez `Logs/Lua.log`
- Recherchez vos messages `print()` dans le log
- Vérifiez l'absence d'erreurs Lua (stack traces)

**Commande de validation syntaxique** (optionnel) :
```bash
luac -p Lua/GameplayScript.lua
```

**En cas d'erreur** :
- Corrigez les erreurs de syntaxe indiquées dans le log
- Vérifiez les appels à l'API Civilization V
- Testez en mode pas à pas avec des `print()` de débogage

### 2.3 Test des modifications SQL

**Objectif** : Vérifier que les requêtes SQL s'exécutent correctement

**Procédure** :
1. Modifiez `SQL/ModSchema.sql`
2. Sauvegardez le fichier
3. Relancez le jeu et le mod

**Vérifications** :
- Consultez `Logs/Database.log`
- Recherchez les requêtes SQL exécutées
- Vérifiez l'absence d'erreurs "Invalid query" ou "No such table"

**En cas d'erreur** :
- Vérifiez les noms de tables et colonnes
- Consultez la documentation du schéma de Civ5
- Testez la requête manuellement si possible

## 3. Tests de stabilité

### 3.1 Test de partie complète

**Objectif** : S'assurer que le mod est stable sur la durée

**Procédure** :
1. Démarrez une nouvelle partie en vitesse Quick
2. Jouez au moins 50 tours
3. Testez différentes actions (combats, diplomatie, construction)
4. Sauvegardez et rechargez la partie

**Résultat attendu** :
- Aucun crash
- Aucun ralentissement notable
- Les sauvegardes se chargent correctement

### 3.2 Test de compatibilité

**Objectif** : Vérifier la compatibilité avec différents modes

**Procédure** :
1. **Solo** : Testez une partie normale
2. **Multijoueur** : Si applicable, testez en ligne
3. **Hotseat** : Testez le mode tour par tour local

**Résultat attendu** : Le mod fonctionne dans tous les modes supportés

### 3.3 Test de désactivation

**Objectif** : S'assurer que la désactivation du mod ne cause pas de problème

**Procédure** :
1. Désactivez le mod dans le menu MODS
2. Lancez une partie normale (sans mod)
3. Vérifiez que le jeu fonctionne normalement

**Résultat attendu** : Le jeu vanilla fonctionne sans trace du mod

## 4. Checklist avant commit

Avant de commiter vos modifications sur Git :

- [ ] ✅ Tous les fichiers XML sont valides (syntaxe correcte)
- [ ] ✅ Tous les scripts Lua se chargent sans erreur
- [ ] ✅ Les requêtes SQL s'exécutent correctement
- [ ] ✅ Une partie de 50+ tours se déroule sans crash
- [ ] ✅ Les logs ne montrent aucune erreur critique
- [ ] ✅ La sauvegarde/chargement fonctionne
- [ ] ✅ Le README.md est à jour
- [ ] ✅ Les fichiers de moins de 500 lignes (si possible)
- [ ] ✅ Pas de code mort ou commenté inutilement

## 5. Localisation des logs

### Windows
```
Documents\My Games\Sid Meier's Civilization 5\Logs\
```

### macOS
```
~/Documents/Aspyr/Sid Meier's Civilization 5/Logs/
```

### Linux
```
~/.local/share/Aspyr/Sid Meier's Civilization 5/Logs/
```

### Fichiers importants
- `Database.log` : Chargement XML et SQL
- `Lua.log` : Exécution des scripts Lua
- `net_message_debug.log` : Problèmes multijoueur

## 6. Outils utiles

### Validation XML
- [XMLValidator.com](https://www.xmlvalidation.com/)
- Éditeur VS Code avec extension XML Tools

### Validation Lua
```bash
# Installer Lua si nécessaire
brew install lua  # macOS
apt install lua5.1  # Linux

# Vérifier la syntaxe
luac -p Lua/GameplayScript.lua
```

### Modding SDK
Le SDK officiel Civilization V (disponible via Steam) fournit des outils supplémentaires :
- ModBuddy (Windows uniquement)
- FireTuner (débogueur en temps réel)

## 7. Troubleshooting courant

### Le mod n'apparaît pas dans la liste
- Vérifiez l'emplacement du dossier
- Vérifiez que le fichier `.modinfo` est à la racine
- Validez la syntaxe XML du `.modinfo`

### Crash au chargement
- Consultez `Database.log` et `Lua.log`
- Commentez les dernières modifications pour isoler le problème
- Vérifiez les références aux types du jeu

### Le mod se charge mais rien ne se passe
- Vérifiez que les Actions sont correctement définies dans `.modinfo`
- Vérifiez que les scripts Lua sont enregistrés aux bons événements
- Ajoutez des `print()` pour tracer l'exécution

## Conclusion

Suivez ces étapes après chaque modification pour garantir la stabilité du mod. En cas de doute, testez sur une configuration minimale avant de complexifier.
