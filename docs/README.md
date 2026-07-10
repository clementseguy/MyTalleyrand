# Documentation technique — MyTalleyrand

## Architecture

```
Civ5 (Lua) ──► ModUserData (SQLite) ──► source ──► watcher ──► coach ──► overlay
                Modding.OpenUserData      lecture RO   polling 0.5s   tour 1 + /10 tours
                SimpleValues(Name,Value)  gamestate    + validation   LLM ou fallback
```

> **Pont de données selon la plateforme.** Sur **macOS (Civ5 Steam/Aspyr)**, le
> contexte Lua du mod n'expose ni `io` ni `os.execute` : il ne peut pas écrire de
> fichier. Le mod persiste donc l'état de partie dans sa base
> `Modding.OpenUserData()` (SQLite, table `SimpleValues`), que le coach lit en
> lecture seule. Un mode `file` (lecture d'un `gamestate.json`) reste disponible
> pour un futur portage Windows. Le format JSON du gamestate est identique dans
> les deux cas. Détails plateforme : voir [MACOS_GUIDE.md](MACOS_GUIDE.md).

### Composants

| Composant | Fichier(s) | Rôle |
|-----------|-----------|------|
| **Mod Lua** | `mod/Lua/GameplayScript.lua` | Contexte `InGameUIAddin` ; à chaque tour, écrit le JSON de gamestate dans la base `ModUserData` (SQLite) via `Modding.OpenUserData` |
| **Source** | `coach/src/gamestate_source.py` | Abstraction de source : `SqliteModUserDataSource` (macOS, défaut) ou `FileGameStateSource` (fichier JSON) |
| **Watcher** | `coach/src/watcher.py` | Poll la source, valide le schéma, déduplique par `turn_id` |
| **Coach** | `coach/src/coach.py` | Décide quand analyser (tour 1, puis tous les 10 tours), applique les préférences et signale les contextes insuffisants |
| **Préférences** | `coach/src/preferences.py` | Persiste l’objectif de victoire et les paramètres de partie détectés |
| **LLM Client** | `coach/src/llm_client.py` | Appels Mistral/OpenAI, retry exponentiel, erreurs actionnables et fallback local |
| **Overlay** | `coach/src/overlay.py` | Affiche conseils via backend PyQt6 runtime + backend texte pour tests/headless |
| **Config** | `coach/src/config.py` | Multi-niveaux : settings.json → coach.user.json → Keychain → env vars |
| **Schéma** | `coach/src/gamestate_schema.py` | Valide gamestate v0.1.0 |
| **Keychain** | `coach/src/keychain.py` | Stockage/récupération/suppression des clés API via `keyring` et le Keychain macOS |
| **Onboarding** | `coach/src/onboarding.py` | Vérifications de premier lancement: chemins Civ5, source SQLite, clé API du provider actif, permission Accessibilité macOS |

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
source              : string (remote, local_fallback ou context_insufficient)
```

## Structure du projet

```
MyTalleyrand/
├── coach/
│   ├── config/settings.json           # config par défaut (chemins, LLM, overlay)
│   ├── config/coach.user.example.json # exemple config utilisateur
│   ├── config/gamestate.schema.v0.json
│   ├── src/                           # modules Python du coach
│   ├── tests/                         # tests pytest
│   └── scripts/                       # run/test/lint + génération exemple utilisateur
├── mod/
│   ├── MyTalleyrand.modinfo
│   ├── Lua/GameplayScript.lua         # export gamestate
│   ├── XML/, SQL/, Art/
│   └── README.md
├── docs/                              # cette documentation
└── scripts/                           # installation, désinstallation, validation et démarrage
```

## Configuration

Configuration lue par le coach :

1. **`coach/config/settings.json`** — valeurs par défaut (chemins, modèle LLM, overlay)
2. **`~/Library/Application Support/MyTalleyrand/coach.user.json`** — prompts personnalisés et autres préférences non sensibles
3. **Dossier d'état coach `mod_export_dir`** — historique, overlay et objectif de victoire choisi dans l’overlay ; ce dossier n'est pas la source gamestate macOS
4. **Keychain macOS** — clés API stockées par `keyring` sous le service `MyTalleyrand`, comptes `mistral` et `openai`
5. **Variables d'environnement** — `TALLEYRAND_MISTRAL_API_KEY`, `TALLEYRAND_OPENAI_API_KEY`, `TALLEYRAND_LLM_MODEL`, etc.

Commandes utiles pour gérer les clés sans relancer l'installateur :

```bash
cd coach
python3 -m src.keychain set mistral  # saisie masquée
python3 -m src.keychain set openai   # saisie masquée
printf "%s" "$TALLEYRAND_MISTRAL_API_KEY" | python3 -m src.keychain set mistral --stdin
python3 -m src.keychain get mistral
python3 -m src.keychain get openai
python3 -m src.keychain delete mistral
python3 -m src.keychain delete openai
```

Le fichier `coach/config/coach.user.example.json` est dérivé des constantes publiques de `src.config`; utilisez `python3 coach/scripts/generate_user_example.py` depuis la racine du dépôt après toute modification des prompts par défaut.

Variables d'environnement disponibles :

| Variable | Défaut | Description |
|----------|--------|-------------|
| `TALLEYRAND_MISTRAL_API_KEY` | Keychain macOS | Clé API Mistral, prioritaire si définie |
| `TALLEYRAND_OPENAI_API_KEY` | Keychain macOS | Clé API OpenAI, prioritaire si définie |
| `TALLEYRAND_LLM_PROVIDER` | `mistral` | Provider LLM |
| `TALLEYRAND_LLM_MODEL` | `mistral-small-latest` | Modèle |
| `TALLEYRAND_LLM_SYSTEM_PROMPT` | (interne) | Prompt système |
| `TALLEYRAND_LLM_USER_PROMPT_TEMPLATE` | (interne) | Template prompt (doit contenir `{victory_focus}` et `{game_state_json}`) |
| `TALLEYRAND_CIV5_DIR` | `~/Library/Application Support/Sid Meier's Civilization 5` | Dossier de données Civ5 (Steam/Aspyr macOS) |
| `TALLEYRAND_GAMESTATE_SOURCE` | `sqlite` | Source de gamestate : `sqlite` (ModUserData) ou `file` |
| `TALLEYRAND_GAMESTATE_DB` | `.../ModUserData/a1b2c3d4-…-1.db` | Base SQLite ModUserData lue en mode `sqlite` |
| `TALLEYRAND_GAMESTATE_FILE` | `.../export/gamestate.json` | Fichier surveillé en mode `file` |
| `TALLEYRAND_LOG_FILE` | `~/talleyrand.log` | Fichier de log |
| `TALLEYRAND_ANALYSIS_INTERVAL_TURNS` | `10` | Fréquence d'analyse ; `1` force une analyse à chaque tour |

## Conventions

- Tous les fichiers source < 500 lignes
- Schéma gamestate versionné (`schema_version`)
- Côté Lua : écriture dans `ModUserData` (SQLite) via `Modding.OpenUserData`, protégée par `pcall` ; jeton de fraîcheur `write_seq` incrémenté à chaque tour
- Côté coach : lecture SQLite en read-only (`mode=ro`) pour cohabiter avec le jeu, tolérante aux verrous/écritures concurrentes
- Retry exponentiel (tenacity) côté LLM avec statut overlay `Reconnexion LLM en cours`
- Fallback local déterministe si LLM indisponible, signalé dans l'overlay avec reprise automatique au prochain tour analysé
- Un nouveau conseil force l'overlay visible même si le joueur l'a fermé au tour précédent
- Contexte insuffisant signalé distinctement avec confiance basse au lieu d’un conseil présenté comme certain
- Tests : `cd coach && python3 -m pytest`
- Validation complète : `./scripts/validate.sh`

## Liens

- [BACKLOG_v0.1.md](BACKLOG_v0.1.md) — backlog initial
- [BACKLOG_v0.2.md](BACKLOG_v0.2.md) — nouvelles tâches debug, recette, Mistral et maintenance
- [BACKLOG_v0.3.md](BACKLOG_v0.3.md) — préparation du partage communauté
- [TESTING.md](TESTING.md) — tests automatisés et manuels
- [MACOS_GUIDE.md](MACOS_GUIDE.md) — spécificités macOS (chemins, permissions, packaging)
- [VENV_DEBUG_AUDIT.md](VENV_DEBUG_AUDIT.md) — conservation temporaire et audit secrets du `.venv`
