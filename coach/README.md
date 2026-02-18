# Coach MyTalleyrand (Python)

Application de coaching en temps réel pour Civilization V.

## Installation

### Option recommandée (depuis la racine du repo)

```bash
./script/install_macos.sh
```

### Option manuelle (développement)

```bash
cd coach
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

## Configuration LLM (clé + prompts)

Le coach lit 2 niveaux de configuration :

1. **Base projet** : `coach/config/settings.json`
2. **Utilisateur local** : `~/Library/Application Support/MyTalleyrand/coach.user.json`

Un exemple est fourni dans `coach/config/coach.user.example.json`.

### Champs configurables

- `llm.api_key` : clé OpenAI.
- `llm.system_prompt` : prompt système complet.
- `llm.user_prompt_template` : template prompt utilisateur (doit contenir `{victory_focus}` et `{game_state_json}`).

> Priorité des variables d'environnement :
> `TALLEYRAND_OPENAI_API_KEY`, `TALLEYRAND_LLM_SYSTEM_PROMPT`, `TALLEYRAND_LLM_USER_PROMPT_TEMPLATE`.

## Lancement

```bash
cd coach
python3 src/main.py
```

Mode one-shot (smoke test) :

```bash
python3 src/main.py --once --victory-focus science
```

## Échange de données mod ↔ coach

- Fichier attendu : `.../MODS/MyTalleyrand/export/gamestate.json`
- Schéma validé : `coach/config/gamestate.schema.v0.json`
- Champs minimum : `schema_version`, `turn_id`, `turn_number`, `timestamp_utc`, `player`, `resources`
- Déduplication par `turn_id`
- Fréquence de refresh watcher : `0.5s`

## Tests

```bash
./scripts/test.sh
./scripts/lint.sh
python3 -m pytest
```
