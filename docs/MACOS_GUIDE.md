# 🍎 Guide technique macOS - MyTalleyrand

**Date :** 22 décembre 2025  
**Version :** 1.0  
**Plateforme cible :** macOS 13+ (Ventura, Sonoma)

---

## 📋 Résumé exécutif

Ce document détaille les spécificités techniques nécessaires pour faire fonctionner MyTalleyrand sur macOS, incluant les choix d'architecture, les permissions système, et les solutions aux limitations de la plateforme.

---

## 🏗️ Architecture choisie

### Vue d'ensemble

```
┌────────────────────────────────────────────┐
│         Civilization V (macOS)             │
│      ~/Library/Application Support/        │
│         Sid Meier's Civilization 5         │
│                                            │
│  [Mod Lua]                                 │
│     ↓ Exporte                              │
│  gamestate.json                            │
└────────────────────────────────────────────┘
              ↓
┌────────────────────────────────────────────┐
│     Application Coach (Python 3.11+)       │
│      ~/Applications/TalleyrandCoach.app    │
│                                            │
│  • watchdog : surveillance fichier         │
│  • openai : appels LLM                     │
│  • PyQt6 : interface overlay               │
│  • keyring : stockage sécurisé clés        │
└────────────────────────────────────────────┘
              ↓
┌────────────────────────────────────────────┐
│          Overlay UI (PyQt6)                │
│    Par-dessus fenêtre Civ5 (mode fenêtré) │
│                                            │
│  • Conseils du coach                       │
│  • Objectifs à 10 tours                    │
│  • Actions recommandées                    │
└────────────────────────────────────────────┘
```

---

## 🔧 Stack technique validée pour macOS

### Python 3.11+ (Recommandé)

**Installation :**
```bash
# Via Homebrew (recommandé)
brew install python@3.11

# Vérification
python3 --version  # 3.11.x
which python3      # /opt/homebrew/bin/python3
```

**Dépendances principales :**
```bash
pip3 install --upgrade pip
pip3 install \
    PyQt6==6.6.1 \
    openai==1.7.0 \
    watchdog==3.0.0 \
    keyring==24.3.0 \
    requests==2.31.0 \
    tenacity==8.2.3
```

**Pourquoi Python ?**
- ✅ Natif sur macOS (via Homebrew)
- ✅ PyQt6 supporte Apple Silicon (M1/M2/M3)
- ✅ Pas de notarization obligatoire pour dev
- ✅ Rapide à prototyper
- ✅ Excellents SDK pour LLM (OpenAI, Anthropic)

**Alternative considérée :**
- Electron + Node.js : Meilleure UI mais complexité accrue (notarization obligatoire)

---

## 📂 Chemins fichiers sur macOS

### Civilization V (version Aspyr)

```bash
# Dossier principal du jeu
/Applications/Civilization V.app/

# Dossier utilisateur (sauvegardes, mods)
~/Documents/Aspyr/Sid Meier's Civilization 5/

# Mods
~/Documents/Aspyr/Sid Meier's Civilization 5/MODS/
└── MyTalleyrand/
    ├── MyTalleyrand.modinfo
    ├── XML/
    ├── Lua/
    └── export/
        └── gamestate.json  # ← Fichier généré par le mod

# Logs du jeu
~/Documents/Aspyr/Sid Meier's Civilization 5/Logs/
├── Database.log
├── Lua.log
└── net_message_debug.log
```

### Application Coach

```bash
# En développement
~/Projects/talleyrand-coach/
├── src/
├── config/
└── logs/

# En production (après packaging)
/Applications/TalleyrandCoach.app/
```

### Fichiers de configuration

```bash
# Préférences utilisateur
~/.config/talleyrand/
├── settings.json
└── cache/

# Clés API (via Keychain)
# Stockées dans macOS Keychain, pas de fichier
```

---

## 🔐 Permissions système requises

### 1. Accessibilité (Accessibility)

**Nécessaire pour :** Détecter la position de la fenêtre Civ5

**Activation :**
```
Préférences Système → Confidentialité et sécurité
→ Accessibilité
→ [+] Ajouter TalleyrandCoach.app
```

**Code Python pour vérifier :**
```python
from ApplicationServices import AXIsProcessTrusted

if not AXIsProcessTrusted():
    print("⚠️ Accès Accessibilité requis")
    print("→ Préférences Système → Accessibilité")
    sys.exit(1)
```

### 2. Accès complet au disque (optionnel)

**Nécessaire si :** Surveillance de fichiers hors Documents

**Alternative :** Utiliser uniquement le dossier Documents (autorisé par défaut)

### 3. Gatekeeper et quarantine

**Problème :** macOS bloque les apps non signées

**Solution développement :**
```bash
# Retirer la quarantine
xattr -d com.apple.quarantine TalleyrandCoach.app

# Ou autoriser dans Préférences Système
# → Sécurité → "Ouvrir quand même"
```

**Solution production :**
```bash
# Code signing (nécessite Developer ID)
codesign --deep --force \
  --sign "Developer ID Application: Votre Nom (TEAM_ID)" \
  TalleyrandCoach.app

# Notarization (macOS 10.15+)
xcrun notarytool submit TalleyrandCoach.zip \
  --apple-id votre@email.com \
  --password app-specific-password \
  --team-id TEAM_ID \
  --wait
```

---

## 🖥️ Overlay : Défis techniques macOS

### Problème : Fenêtre plein écran

**Limitation :** macOS gère le plein écran de manière spéciale (Mission Control)

**Solution :**
```markdown
Civ5 DOIT être en mode fenêtré pour que l'overlay fonctionne.

Configuration dans Civ5 :
Settings → Video → Display Mode → Windowed
ou
Windowed Fullscreen (borderless)
```

### Implémentation PyQt6

```python
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor

class TalleyrandOverlay(QWidget):
    def __init__(self):
        super().__init__()
        
        # Flags essentiels pour overlay macOS
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |   # Toujours au-dessus
            Qt.WindowType.FramelessWindowHint |    # Sans bordure
            Qt.WindowType.Tool |                    # Pas dans Dock
            Qt.WindowType.WindowTransparentForInput  # Clics passthrough
        )
        
        # Transparence
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Support Retina
        self.setAttribute(Qt.WidgetAttribute.WA_NativeWindow)
        
        # Position initiale
        self.resize(400, 600)
        self.move(100, 100)
```

### Détection fenêtre Civ5 (macOS spécifique)

```python
import Quartz
from AppKit import NSWorkspace

def find_civ5_window():
    """
    Trouve la fenêtre Civilization V sur macOS
    
    Returns:
        dict: Position et taille de la fenêtre
    """
    options = Quartz.kCGWindowListOptionOnScreenOnly
    window_list = Quartz.CGWindowListCopyWindowInfo(
        options, 
        Quartz.kCGNullWindowID
    )
    
    for window in window_list:
        owner = window.get('kCGWindowOwnerName', '')
        
        # Civ5 peut avoir différents noms selon la version
        if any(name in owner for name in ['Civilization V', 'Civ5', 'Sid Meier']):
            bounds = window['kCGWindowBounds']
            return {
                'x': int(bounds['X']),
                'y': int(bounds['Y']),
                'width': int(bounds['Width']),
                'height': int(bounds['Height']),
                'pid': window.get('kCGWindowOwnerPID')
            }
    
    return None

# Utilisation
civ5_pos = find_civ5_window()
if civ5_pos:
    overlay.move(civ5_pos['x'] + 20, civ5_pos['y'] + 20)
```

### Gestion multi-écrans

```python
from PyQt6.QtGui import QScreen
from PyQt6.QtWidgets import QApplication

def get_screen_for_window(window_x: int, window_y: int) -> QScreen:
    """
    Détermine l'écran contenant une fenêtre
    """
    for screen in QApplication.screens():
        geometry = screen.geometry()
        if geometry.contains(window_x, window_y):
            return screen
    
    # Fallback : écran principal
    return QApplication.primaryScreen()

# Positionner sur le bon écran
civ5_pos = find_civ5_window()
if civ5_pos:
    screen = get_screen_for_window(civ5_pos['x'], civ5_pos['y'])
    overlay.setScreen(screen)
```

---

## 🔍 Surveillance de fichiers

### Watchdog sur macOS

```python
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path

class GameStateHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback
        self.last_modified = 0
        
    def on_modified(self, event):
        if event.src_path.endswith('gamestate.json'):
            # Debounce : éviter les doubles notifications
            now = time.time()
            if now - self.last_modified > 0.5:
                self.last_modified = now
                self.callback(event.src_path)

# Setup
export_dir = Path.home() / "Documents/Aspyr/Sid Meier's Civilization 5/MODS/MyTalleyrand/export"

handler = GameStateHandler(callback=process_new_turn)
observer = Observer()
observer.schedule(handler, str(export_dir), recursive=False)
observer.start()

print(f"👁️  Surveillance de {export_dir}")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
    
observer.join()
```

**Performance macOS :**
- ✅ FSEvents natif (très efficace)
- ✅ CPU < 1% en idle
- ✅ Détection < 100ms

---

## 🔑 Stockage sécurisé des clés API

### macOS Keychain

```python
import keyring

# Configuration
SERVICE_NAME = "MyTalleyrand"

# Stocker une clé API
def save_api_key(provider: str, key: str):
    """
    Stocke une clé API dans le Keychain macOS
    
    Args:
        provider: 'openai', 'anthropic', etc.
        key: La clé API
    """
    keyring.set_password(SERVICE_NAME, f"{provider}_api_key", key)
    print(f"✅ Clé {provider} sauvegardée dans Keychain")

# Récupérer une clé API
def get_api_key(provider: str) -> str:
    """
    Récupère une clé API du Keychain
    
    Returns:
        La clé API ou None si non trouvée
    """
    key = keyring.get_password(SERVICE_NAME, f"{provider}_api_key")
    if not key:
        print(f"⚠️ Clé {provider} non trouvée dans Keychain")
    return key

# Supprimer une clé
def delete_api_key(provider: str):
    """Supprime une clé du Keychain"""
    try:
        keyring.delete_password(SERVICE_NAME, f"{provider}_api_key")
        print(f"🗑️ Clé {provider} supprimée")
    except keyring.errors.PasswordDeleteError:
        print(f"⚠️ Clé {provider} introuvable")

# Utilisation
save_api_key("openai", "sk-proj-...")
api_key = get_api_key("openai")
```

**Avantages Keychain :**
- ✅ Chiffrement natif macOS
- ✅ Synchronisation iCloud (si activé)
- ✅ Pas de fichier config en clair
- ✅ Accessible via Trousseau (app native)

---

## 🚀 Packaging et distribution

### Développement : Script de lancement

```bash
#!/bin/bash
# start_coach.command

# Naviguer vers le dossier du projet
cd "$(dirname "$0")"

# Activer environnement virtuel
source venv/bin/activate

# Lancer l'application
python3 src/main.py

# Garder le terminal ouvert
echo ""
echo "Coach fermé. Appuyez sur une touche pour quitter."
read
```

Rendre exécutable :
```bash
chmod +x start_coach.command
```

**Avantage :** Double-clic pour lancer (comme une app)

### Production : py2app

```bash
# Installer py2app
pip3 install py2app

# Créer setup.py
```

```python
# setup.py
from setuptools import setup

APP = ['src/main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'packages': ['PyQt6', 'openai', 'watchdog', 'keyring'],
    'iconfile': 'assets/icon.icns',
    'plist': {
        'CFBundleName': 'TalleyrandCoach',
        'CFBundleDisplayName': 'Talleyrand Coach',
        'CFBundleIdentifier': 'com.clementseguy.talleyrand',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '13.0',
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
```

```bash
# Build
python3 setup.py py2app

# Résultat
ls dist/
TalleyrandCoach.app  # ← Application macOS native
```

### Distribution : DMG

```bash
# Créer une image disque
hdiutil create -volname "Talleyrand Coach" \
  -srcfolder dist/TalleyrandCoach.app \
  -ov -format UDZO \
  TalleyrandCoach-1.0.0.dmg
```

---

## 🐛 Debugging sur macOS

### Logs système

```bash
# Logs Console.app (filtrer par "TalleyrandCoach")
# Applications → Utilitaires → Console

# Logs Python
tail -f ~/talleyrand.log

# Logs Civilization V
tail -f ~/Documents/Aspyr/Sid\ Meier\'s\ Civilization\ 5/Logs/Lua.log
```

### Instruments (profiling)

```bash
# Profiler l'app
instruments -t "Time Profiler" dist/TalleyrandCoach.app

# Vérifier fuites mémoire
instruments -t "Leaks" dist/TalleyrandCoach.app
```

### lldb (debugger)

```bash
# Lancer avec debugger
lldb -- python3 src/main.py

# Commandes utiles
(lldb) run
(lldb) bt      # backtrace
(lldb) c       # continue
```

---

## ⚡ Optimisations macOS

### 1. Support Apple Silicon (M1/M2/M3)

```bash
# Vérifier architecture
arch
# arm64 = Apple Silicon natif
# x86_64 = Intel ou Rosetta

# Forcer architecture native
arch -arm64 python3 src/main.py
```

**PyQt6** supporte nativement arm64 ✅

### 2. Retina / HiDPI

```python
# Activer support HiDPI
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)

app = QApplication(sys.argv)
```

### 3. Mode sombre (Dark Mode)

```python
# Détecter le thème système
from PyQt6.QtGui import QPalette

palette = QApplication.palette()
is_dark = palette.color(QPalette.ColorRole.Window).lightness() < 128

if is_dark:
    # Appliquer style dark
    app.setStyleSheet("QWidget { background-color: #2b2b2b; color: white; }")
```

### 4. Économie d'énergie

```python
import time

class EfficientWatcher:
    def __init__(self):
        self.last_check = 0
        self.check_interval = 2.0  # secondes
        
    def should_check(self) -> bool:
        now = time.time()
        if now - self.last_check >= self.check_interval:
            self.last_check = now
            return True
        return False
```

---

## 🧪 Tests sur macOS

### Environnements de test

```bash
# macOS 13 (Ventura)
# macOS 14 (Sonoma)
# macOS 15 (Sequoia beta)

# Architectures
# Intel x86_64
# Apple Silicon arm64
```

### Checklist de validation

- [ ] Installation fraîche Python 3.11
- [ ] Installation dépendances via pip
- [ ] Lancement application
- [ ] Détection Civilization V
- [ ] Overlay s'affiche correctement
- [ ] Permissions Accessibilité demandées
- [ ] Keychain stocke/récupère clé API
- [ ] Surveillance gamestate.json fonctionne
- [ ] Appel LLM réussi
- [ ] Performance CPU < 5%
- [ ] Pas de crash après 1h
- [ ] Fonctionne sur écran Retina
- [ ] Fonctionne en dual-screen

---

## 📚 Ressources

### Documentation Apple

- [macOS Security](https://developer.apple.com/documentation/security)
- [Gatekeeper and Notarization](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)
- [Keychain Services](https://developer.apple.com/documentation/security/keychain_services)

### PyQt6

- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [Qt for macOS](https://doc.qt.io/qt-6/macos.html)

### Civilization V Modding

- [CivFanatics Modding Forum](https://forums.civfanatics.com/forums/civ5-creation-customization.388/)
- [Civilization V SDK Documentation](http://modiki.civfanatics.com/)

---

## 🆘 Support

### Problèmes fréquents

**Q : L'overlay ne s'affiche pas**
```
R : 
1. Vérifier que Civ5 est en mode fenêtré
2. Donner accès "Accessibilité" dans Préférences Système
3. Vérifier que l'app est lancée (ps aux | grep talleyrand)
```

**Q : gamestate.json non généré**
```
R :
1. Vérifier que le mod est activé dans Civ5
2. Consulter ~/Documents/Aspyr/.../Logs/Lua.log
3. Vérifier permissions du dossier export/
```

**Q : Erreur "Operation not permitted"**
```
R :
1. Désactiver SIP temporairement (dev uniquement)
   csrutil disable  # Redémarrer en Recovery Mode
2. Ou donner "Full Disk Access" à Terminal.app
```

**Q : PyQt6 ne s'installe pas sur M1**
```
R :
1. S'assurer d'utiliser Python arm64 natif
   python3 -c "import platform; print(platform.machine())"
   # Doit afficher "arm64"
2. Réinstaller avec pip arm64
   arch -arm64 pip3 install PyQt6
```

---

**Dernière mise à jour :** 22 décembre 2025  
**Mainteneur :** Clément Séguy  
**Licence :** À définir
