# Documentation technique — MyTalleyrand

## Architecture

```
Civ5 (Lua) ──► gamestate.json ──► watcher ──► coach ──► overlay
                 écriture atomique       polling 0.5s     tour 1 + /10 tours
                 tmp + rename            + validation     LLM ou fallback
```

### Composants

| Composant | Fichier(s) | Rôle |
|-----------|-----------|------|
| **Mod Lua** | `mod/Lua/GameplayScript.lua` | Exporte `gamestate.json` à chaque tour (écriture atomique, `pcall`) |
| **Watcher** | `coach/src/watcher.py` | Poll le fichier, valide le schéma, déduplique par `turn_id` |
| **Coach** | `coach/src/coach.py` | Décide quand analyser (tour 1, puis tous les 10 tours) |
| **LLM Client** | `coach/src/llm_client.py` | Appel OpenAI + retry exponentiel, statuts UX réseau et fallback local |
| **Overlay** | `coach/src/overlay.py` | Affiche conseils (abstraction testable, pas de PyQt6 runtime) |
| **Config** | `coach/src/config.py` | Multi-niveaux : settings.json → coach.user.json → Keychain → env vars |
| **Schéma** | `coach/src/gamestate_schema.py` | Valide gamestate v0.1.0 |
| **Keychain** | `coach/src/keychain.py` | Stockage/récupération/suppression des clés API via `keyring` et le Keychain macOS |

### Format gamestate (v0.1.0)

```json
{
  "schema_version": "0.1.0",
  "turn_id": 42, "turn_number": 42,
  "timestamp_utc": "2026-01-01T12:00:00Z",
  "player": { "id": 0, "civilization": "CIVILIZATION_FRANCE", "leader": "LEADER_NAPOLEON" },
  "resources": { "gold": 350, "science": 120 }
}
```

### Format de sortie coach (LLMAdvice)

```
objective_10_turns  : string
priority_actions    : list[str] (3-5 items)
risks               : list[str]
confidence          : int (0-100)
categories          : dict (economie/science/militaire/diplomatie → list[str])
source              : string (remote ou local_fallback)
```

## Structure du projet

```
MyTalleyrand/
├── coach/
│   ├── config/settings.json           # config par défaut (chemins, LLM, overlay)
│   ├── config/coach.user.example.json # exemple config utilisateur
│   ├── config/gamestate.schema.v0.json
│   ├── src/                           # 8 modules Python (803 lignes)
│   ├── tests/                         # 7 fichiers pytest (390 lignes)
│   └── scripts/                       # run.sh, test.sh, lint.sh, first_test.sh
├── mod/
│   ├── MyTalleyrand.modinfo
│   ├── Lua/GameplayScript.lua         # 125 lignes — export gamestate
│   ├── XML/, SQL/, Art/
│   └── README.md
├── docs/                              # cette documentation
└── scripts/                           # installation, validation et démarrage
```

## Configuration

Configuration lue par le coach :

1. **`coach/config/settings.json`** — valeurs par défaut (chemins, modèle LLM, overlay)
2. **`~/Library/Application Support/MyTalleyrand/coach.user.json`** — prompts personnalisés et autres préférences non sensibles
3. **Keychain macOS** — clé API OpenAI stockée par `keyring` sous le service `MyTalleyrand`
4. **Variables d'environnement** — `TALLEYRAND_OPENAI_API_KEY`, `TALLEYRAND_LLM_MODEL`, etc. La variable `TALLEYRAND_OPENAI_API_KEY` reste prioritaire pour le développement/CI.

Variables d'environnement disponibles :

| Variable | Défaut | Description |
|----------|--------|-------------|
| `TALLEYRAND_OPENAI_API_KEY` | Keychain macOS | Clé API OpenAI, prioritaire si définie |
| `TALLEYRAND_LLM_PROVIDER` | `openai` | Provider LLM |
| `TALLEYRAND_LLM_MODEL` | `gpt-4o-mini` | Modèle |
| `TALLEYRAND_LLM_SYSTEM_PROMPT` | (interne) | Prompt système |
| `TALLEYRAND_LLM_USER_PROMPT_TEMPLATE` | (interne) | Template prompt (doit contenir `{victory_focus}` et `{game_state_json}`) |
| `TALLEYRAND_CIV5_DIR` | `~/Documents/Aspyr/...` | Dossier Civ5 |
| `TALLEYRAND_GAMESTATE_FILE` | `.../export/gamestate.json` | Fichier surveillé |
| `TALLEYRAND_LOG_FILE` | `~/talleyrand.log` | Fichier de log |

## Conventions

- Tous les fichiers source < 500 lignes
- Schéma gamestate versionné (`schema_version`)
- Écriture atomique (tmp + rename) côté Lua avec `pcall` pour crash-safety
- Retry exponentiel (tenacity) côté LLM avec statut overlay `Reconnexion LLM en cours`
- Fallback local déterministe si LLM indisponible, signalé dans l'overlay avec reprise automatique au prochain tour analysé
- Tests : `cd coach && python3 -m pytest`
- Validation complète : `./scripts/validate.sh`

## Liens

- [BACKLOG.md](BACKLOG.md) — statuts des US et travail restant
- [TESTING.md](TESTING.md) — tests automatisés et manuels
- [MACOS_GUIDE.md](MACOS_GUIDE.md) — spécificités macOS (chemins, permissions, packaging)
