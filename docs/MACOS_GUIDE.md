# Guide macOS — MyTalleyrand

Spécificités macOS pour le développement et l'utilisation de MyTalleyrand.

## Chemins fichiers

### Civilization V (Aspyr)

```bash
# Dossier utilisateur Civ5
~/Documents/Aspyr/Sid Meier's Civilization 5/

# Mods
~/Documents/Aspyr/Sid Meier's Civilization 5/MODS/MyTalleyrand/

# Export gamestate (généré par le mod)
~/Documents/Aspyr/Sid Meier's Civilization 5/MODS/MyTalleyrand/export/gamestate.json

# Logs Civ5
~/Documents/Aspyr/Sid Meier's Civilization 5/Logs/
```

### Coach (après installation)

```bash
# Application installée
~/Applications/MyTalleyrandCoach/coach/

# Configuration utilisateur
~/Library/Application Support/MyTalleyrand/coach.user.json

# Log coach
~/talleyrand.log
```

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
- La position, l'état visible/masqué et l'état réduit sont persistés dans `overlay_state.json` dans le dossier d'export du mod.
- Un nouveau conseil restaure automatiquement l'overlay réduit afin de ne pas manquer une analyse importante.
- L'interface utilise uniquement du texte, des couleurs et une typographie système/libre : aucun asset Civilization V/Firaxis n'est embarqué. La police `Inter` est utilisée si elle est déjà installée ; sinon Qt applique le fallback Helvetica/Arial/sans-serif.

## Watcher

L'implémentation actuelle utilise un polling simple (`time.sleep(0.5)` + `stat.st_mtime_ns`).

`watchdog` n'est plus dans `requirements.txt`. Une migration vers watchdog (FSEvents natif) reste une amélioration future.

## Keychain

`coach/src/keychain.py` utilise `keyring` pour stocker, lire et supprimer la clé API dans le Keychain macOS.

Priorité de résolution de la clé API :
1. Variable d'environnement `TALLEYRAND_OPENAI_API_KEY` (développement/CI)
2. Keychain macOS, service `MyTalleyrand`, compte `openai`
3. Ancien champ `coach.user.json` → `llm.api_key` seulement pour compatibilité de migration, avec avertissement dans les logs

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

## Troubleshooting

| Problème | Solution |
|----------|----------|
| Overlay invisible | Civ5 en mode fenêtré + permissions Accessibilité |
| `gamestate.json` non généré | Vérifier mod activé + `Lua.log` + permissions dossier `export/` |
| `Operation not permitted` | Donner « Full Disk Access » à Terminal.app |
| PyQt6 ne s'installe pas sur M1 | Vérifier que Python est arm64 natif (pas Rosetta) |
| `pip install` échoue | Utiliser le venv : `.venv/bin/pip install -r requirements.txt` |
