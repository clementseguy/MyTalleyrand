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

**Prérequis :** Civilization V doit tourner en **mode fenêtré** (Settings → Video → Windowed ou Windowed Fullscreen).

L'overlay actuel est une abstraction testable sans UI graphique. L'implémentation PyQt6 future utilisera :

```python
self.setWindowFlags(
    Qt.WindowType.WindowStaysOnTopHint |   # Toujours au-dessus
    Qt.WindowType.FramelessWindowHint |    # Sans bordure
    Qt.WindowType.Tool                     # Pas dans le Dock
)
self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
```

## Watcher

L'implémentation actuelle utilise un polling simple (`time.sleep(0.5)` + `stat.st_mtime_ns`).

`watchdog` n'est plus dans `requirements.txt`. Une migration vers watchdog (FSEvents natif) reste une amélioration future.

## Keychain

`coach/src/keychain.py` lève `NotImplementedError` — l'intégration `keyring` n'est pas encore active.

La clé API est configurée via :
1. `coach.user.json` → `llm.api_key`
2. Variable d'environnement `TALLEYRAND_OPENAI_API_KEY`

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
