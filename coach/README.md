# 🤖 Talleyrand Coach Application

Application Python de coaching en temps réel pour Civilization V.

## 📦 Architecture

```
coach/
├── src/                    # Code source
│   ├── __init__.py
│   ├── main.py            # Point d'entrée
│   ├── watcher.py         # Surveillance gamestate.json
│   ├── overlay.py         # Interface PyQt6
│   ├── coach.py           # Moteur LLM
│   ├── config.py          # Configuration
│   └── keychain.py        # Gestion clés API
├── tests/                 # Tests unitaires
│   ├── __init__.py
│   └── test_config.py
├── config/                # Fichiers de configuration
├── logs/                  # Logs d'exécution
├── requirements.txt       # Dépendances Python
└── README.md             # Ce fichier
```

## 🚀 Installation

### Prérequis

- macOS 13+ (Ventura ou supérieur)
- Python 3.11+
- Homebrew (recommandé)

### Installation Python

```bash
# Via Homebrew
brew install python@3.11

# Vérification
python3 --version  # Doit afficher 3.11.x
```

### Installation des dépendances

```bash
cd coach
pip3 install -r requirements.txt
```

## ⚙️ Configuration

### 1. Clé API LLM

```bash
# Lancer l'assistant de configuration
python3 src/main.py --setup

# Ou manuellement via Python
python3 -c "
from src.keychain import save_api_key
save_api_key('openai', 'sk-proj-...')
"
```

### 2. Permissions macOS

L'application nécessite l'accès **Accessibilité** :

1. `Préférences Système` → `Confidentialité et sécurité`
2. `Accessibilité`
3. Cliquer `+` et ajouter `Terminal.app` (en dev) ou `TalleyrandCoach.app` (en prod)

## 🎮 Utilisation

### Lancement

```bash
cd coach
python3 src/main.py
```

### Workflow

1. Lancer l'application coach
2. Démarrer Civilization V en **mode fenêtré**
3. Charger une partie avec le mod MyTalleyrand activé
4. L'overlay apparaît automatiquement avec les conseils

### Arrêt

```
Ctrl+C dans le terminal
```

## 🧪 Tests

```bash
# Tests unitaires
cd coach
python3 -m pytest tests/

# Avec couverture
python3 -m pytest --cov=src tests/
```

## 📝 Logs

Les logs sont écrits dans :
- `~/talleyrand.log` (logs applicatifs)
- `coach/logs/` (logs de debug)

Consulter les logs :
```bash
tail -f ~/talleyrand.log
```

## 🐛 Debugging

### L'overlay ne s'affiche pas

1. Vérifier que Civ5 est en mode fenêtré
2. Donner accès Accessibilité dans Préférences Système
3. Consulter les logs : `tail -f ~/talleyrand.log`

### gamestate.json non détecté

1. Vérifier que le mod est activé dans Civ5
2. Vérifier le chemin : `~/Documents/Aspyr/Sid Meier's Civilization 5/MODS/MyTalleyrand/export/gamestate.json`
3. Consulter Lua.log du jeu

## 📚 Documentation

- [Guide technique macOS](../docs/MACOS_GUIDE.md)
- [Backlog et User Stories](../docs/BACKLOG.md)
- [Architecture complète](../docs/SUMMARY.md)

## 🔗 Liens utiles

- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Watchdog Documentation](https://pythonhosted.org/watchdog/)

---

**Version :** 0.1.0  
**Auteur :** Clément Séguy  
**Licence :** À définir
