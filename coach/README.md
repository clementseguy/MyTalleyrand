# 🤖 Talleyrand Coach Application

Application Python de coaching en temps réel pour Civilization V.

## 📦 Architecture

```
coach/
├── src/                    # Code source
│   ├── __init__.py
│   ├── main.py            # Point d'entrée
│   ├── watcher.py         # Surveillance gamestate.json
│   ├── overlay.py         # Overlay MVP (état persistant + rendu texte)
│   ├── coach.py           # Logique coach (tour 1 / tous les 10 tours + historique)
│   ├── llm_client.py      # Sortie LLM structurée + fallback local
│   ├── config.py          # Configuration
│   └── keychain.py        # Gestion clés API
├── tests/                 # Tests unitaires
│   ├── __init__.py
│   └── test_config.py
├── config/                # settings.json + schéma gamestate v0
├── logs/                  # Logs d'exécution
├── scripts/               # Scripts run/test/lint
├── requirements.txt       # Dépendances Python
└── README.md              # Ce fichier
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
python3 src/main.py --once --victory-focus science

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
./scripts/run.sh
```

### Workflow

1. Lancer l'application coach
2. Démarrer Civilization V en **mode fenêtré**
3. Charger une partie avec le mod MyTalleyrand activé
4. Le coach déclenche une analyse au tour 1 puis tous les 10 tours
5. L'overlay affiche l'objectif 10 tours et les actions prioritaires

### Arrêt

```
Ctrl+C dans le terminal
```

## 🧪 Tests

```bash
./scripts/test.sh

# Premier lancement local (sans Civ5)
./scripts/first_test.sh

# Suite phase 3/4/5
python3 -m pytest tests/test_overlay.py tests/test_coach_engine.py tests/test_pipeline_integration.py

# Lint (vérification syntaxique Python)
./scripts/lint.sh
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

**Version :** 0.3.1  
**Auteur :** Clément Séguy  
**Licence :** À définir
