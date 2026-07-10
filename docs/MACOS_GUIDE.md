# Guide macOS — MyTalleyrand

Spécificités macOS pour le développement et l'utilisation de MyTalleyrand.

## Chemins fichiers

### Civilization V (Steam / Aspyr)

Sur la version **Steam macOS (portage Aspyr)**, le dossier de données actif est
sous `~/Library/Application Support/` (le jeu le voit en interne comme
`C:\Emu\AppDataParent\…` via l'émulation Windows) — **pas** `~/Documents/Aspyr/`.

```bash
CIV="$HOME/Library/Application Support/Sid Meier's Civilization 5"

# Dossier de données Civ5 :            "$CIV"
# Mods :                               "$CIV/MODS/MyTalleyrand/"
# Données exportées par le mod (SQLite):
#   "$CIV/ModUserData/a1b2c3d4-e5f6-7890-abcd-ef1234567890-1.db"  (table SimpleValues)
# Logs Civ5 :                          "$CIV/Logs/"  (Lua.log, Modding.log, Database.log)
# Config de debug :                    "$CIV/config.ini"
# Cache des mods :                     "$CIV/cache/"  (Civ5ModsDatabase.db)
```

> L'ancien chemin `~/Documents/Aspyr/…` correspond au Store Aspyr autonome, pas à
> la version Steam. Installer le mod aux deux endroits provoque des erreurs
> `UNIQUE constraint failed: ModFiles` — n'utiliser que le dossier Library ci-dessus.

### Coach (après installation)

```bash
# Application installée
~/Applications/MyTalleyrandCoach/coach/

# Configuration utilisateur
~/Library/Application Support/MyTalleyrand/coach.user.json

# Log coach
~/talleyrand.log
```

## Premier lancement

Après installation, lancez un diagnostic guidé sans démarrer la boucle de surveillance :

```bash
cd ~/Applications/MyTalleyrandCoach/coach
.venv/bin/python src/main.py --onboarding
```

Le coach exécute aussi automatiquement ces vérifications au premier démarrage graphique et crée `.onboarding_done` dans le dossier d'état du coach. Les contrôles couvrent le dossier Civ5, la source SQLite, la présence éventuelle d’une clé du provider actif et la permission Accessibilité macOS.

## Désinstallation

```bash
./scripts/uninstall_macos.sh
# supprimer aussi configuration utilisateur et logs
REMOVE_USER_DATA=1 REMOVE_LOGS=1 ./scripts/uninstall_macos.sh
```

Le script supprime `~/Applications/MyTalleyrandCoach`, `MODS/MyTalleyrand` et tente de supprimer les clés `mistral` et `openai` du service Keychain `MyTalleyrand`. Par défaut il conserve `~/Library/Application Support/MyTalleyrand` et `~/talleyrand.log` pour éviter une suppression accidentelle de préférences ou d’historique.

## Permissions requises

### Accessibilité (pour overlay graphique futur)

Nécessaire pour détecter la position de la fenêtre Civ5 :

```
Réglages Système → Confidentialité et sécurité → Accessibilité → [+] ajouter l'app
```

### Gatekeeper (apps non signées)

```bash
# Retirer la quarantine
xattr -d com.apple.quarantine TalleyrandCoach.app

# Ou : Réglages Système → Sécurité → "Ouvrir quand même"
```

### Accès fichiers

Le dossier `~/Documents/` est autorisé par défaut. Pas besoin de « Full Disk Access » pour le fonctionnement normal.

## Overlay

**Prérequis :** Civilization V doit tourner en **mode fenêtré** (Settings → Video → Windowed ou Windowed Fullscreen). Les pleins écrans exclusifs macOS peuvent empêcher une fenêtre tierce de rester visible au-dessus du jeu.

Le coach utilise PyQt6 pour afficher une fenêtre transparente, sans bordure, toujours au-dessus. Au démarrage, il vérifie la permission macOS **Accessibilité** (`AXIsProcessTrusted`) et journalise les écrans détectés pour faciliter le diagnostic multi-écrans.

- Accordez la permission **Réglages Système → Confidentialité et sécurité → Accessibilité** au terminal ou au lanceur utilisé pour démarrer le coach si macOS le demande.
- Les boutons `–` et `×` réduisent ou masquent seulement l'overlay : l'application continue de surveiller les nouveaux tours.
- La position, l'état visible/masqué et l'état réduit sont persistés dans `overlay_state.json`.
- `–` réduit l'overlay sans le masquer ; `×` le masque pour le tour courant. Dans les deux cas, un nouveau conseil force `visible=true` et réaffiche l'overlay afin de ne pas manquer une analyse importante.
- Le bas de la carte affiche le budget LLM cumulé estimé pour la partie en cours; un marqueur ⚠️ apparaît quand 80% du plafond `coach.cost_limit_usd` est atteint.
- L'interface utilise uniquement du texte, des couleurs et une typographie système/libre : aucun asset Civilization V/Firaxis n'est embarqué. La police `Inter` est utilisée si elle est déjà installée ; sinon Qt applique le fallback Helvetica/Arial/sans-serif.

## Watcher

L'implémentation actuelle utilise un polling simple (`time.sleep(0.5)` + `stat.st_mtime_ns`).

`watchdog` n'est plus dans `requirements.txt`. Une migration vers watchdog (FSEvents natif) reste une amélioration future.

## Keychain

`coach/src/keychain.py` utilise `keyring` pour stocker, lire et supprimer la clé API dans le Keychain macOS.

Priorité de résolution de la clé API :
1. Variable d'environnement `TALLEYRAND_MISTRAL_API_KEY` ou `TALLEYRAND_OPENAI_API_KEY`
2. Keychain macOS, service `MyTalleyrand`, compte `mistral` ou `openai`
3. Champ `coach.user.json` → `llm.api_keys.<provider>` seulement pour migration locale, avec avertissement dans les logs

## Lancement depuis le dépôt et mode debug

Pour recetter les changements du dépôt courant sans utiliser la copie installée dans `~/Applications` :

```bash
./scripts/run_coach.sh --debug
./scripts/run_coach.sh --interval 1
```

`--debug` est un raccourci pour analyser chaque tour et augmenter la verbosité des logs. Équivalent env :

```bash
TALLEYRAND_ANALYSIS_INTERVAL_TURNS=1 ./scripts/run_coach.sh
```

Le script échoue explicitement si `coach/.venv/bin/python` est absent ou cassé.

## Apple Silicon

PyQt6 supporte nativement arm64 (M1/M2/M3/M4). Vérifier l'architecture Python :

```bash
python3 -c "import platform; print(platform.machine())"  # arm64
```

## Packaging futur

```bash
# py2app
pip3 install py2app
python3 setup.py py2app  # → dist/TalleyrandCoach.app

# Code signing
codesign --deep --force --sign "Developer ID Application: ..." TalleyrandCoach.app

# Notarization
xcrun notarytool submit TalleyrandCoach.zip --apple-id ... --team-id ... --wait

# DMG
hdiutil create -volname "Talleyrand Coach" -srcfolder dist/TalleyrandCoach.app -ov -format UDZO TalleyrandCoach.dmg
```

## Mod Civ5 — packaging et debug (macOS/Aspyr)

Le portage Steam/Aspyr impose plusieurs contraintes non évidentes, découvertes en
production. À respecter sous peine que le mod « s'active » mais n'exécute rien.

### Contraintes de packaging (`.modinfo`)

- **Chemins des fichiers en contenu texte, avec antislash** :
  `<File md5="…" import="0">Lua\GameplayScript.lua</File>`.
  Le format `<File … source="Lua/GameplayScript.lua"/>` **n'est pas parsé** (aucun
  fichier enregistré → le mod ne charge pas son Lua). Régénérer le `md5` à chaque
  changement (le jeu le valide).
- **Point d'entrée `InGameUIAddin` → un fichier `.xml`**, jamais un `.lua` brut
  (sinon crash `InGame.lua:… attempt to index local 'addinFile' (a nil value)` qui
  casse tout le chargement des addins). Le moteur exécute automatiquement le `.lua`
  de **même nom de base** dans le même dossier. Le `<Context>` doit contenir au
  moins un contrôle réel (une `<Box Hidden="1"/>` suffit).
- **Un seul emplacement d'installation** : `…/Library/…/MODS/MyTalleyrand`.

### Pas d'écriture fichier depuis le Lua

Le contexte Lua UI n'expose ni `io` ni `os.execute`, **même avec
`EnableLuaDebugLibrary = 1`**. Le mod écrit donc via `Modding.OpenUserData()` dans
une base SQLite (`ModUserData/<ModID>-<version>.db`, table `SimpleValues`) que le
coach lit. C'est le mode `sqlite` (défaut) de `coach/src/gamestate_source.py`.

### Activer les logs et diagnostiquer

```bash
CIV="$HOME/Library/Application Support/Sid Meier's Civilization 5"

# 1. Activer logs + debug (jeu fermé). Le jeu réécrit config.ini à la fermeture :
#    on verrouille le fichier en lecture seule pour que les flags tiennent.
./scripts/enable_debug.sh

# 2. Après TOUT changement du .modinfo, purger le cache (sinon entrées obsolètes) :
#    scripts/enable_debug.sh le fait aussi.

# 3. Lancer le jeu via le menu Mods, jouer un tour, puis vérifier :
grep -i talleyrand "$CIV/Logs/Lua.log"                 # traces d'exécution du mod
grep -i constraint "$CIV/Logs/Modding.log"             # doit être vide
sqlite3 "$CIV/ModUserData/a1b2c3d4-e5f6-7890-abcd-ef1234567890-1.db" \
  "SELECT Name FROM SimpleValues;"                     # doit lister gamestate_json
```

Toujours démarrer la partie **depuis le menu Mods** (pas le menu principal), sinon
le mod n'est pas chargé dans la session.

## Troubleshooting

| Problème | Solution |
|----------|----------|
| Overlay invisible | Civ5 en mode fenêtré + permissions Accessibilité |
| Base `ModUserData` vide / absente | Mod activé via le **menu Mods** ? Traces `[MyTalleyrand]` dans `Lua.log` ? Voir section packaging ci-dessous |
| Coach « Source introuvable » | Vérifier `TALLEYRAND_GAMESTATE_DB` / le fichier `ModUserData/…-1.db` et que le jeu a lancé au moins un tour |
| `Operation not permitted` | Donner « Full Disk Access » à Terminal.app |
| PyQt6 ne s'installe pas sur M1 | Vérifier que Python est arm64 natif (pas Rosetta) |
| `pip install` échoue | Utiliser le venv : `.venv/bin/pip install -r requirements.txt` |


## Stratégie de victoire et contexte insuffisant

Au tour 1, l’overlay PyQt6 demande l’objectif de victoire. Le bouton ⚙ permet ensuite de changer cette stratégie en cours de partie ; le changement est sauvegardé dans `user_preferences.json` dans le dossier export du mod et appliqué à la prochaine analyse.

Si l’overlay affiche **Contexte insuffisant**, le coach a volontairement réduit sa confiance parce que le gamestate exporté ne contient pas encore assez d’informations (par exemple aucune ville, unités absentes ou paramètres de partie manquants). Vérifiez que le mod est activé et consultez `Lua.log` si le message persiste après plusieurs tours.
