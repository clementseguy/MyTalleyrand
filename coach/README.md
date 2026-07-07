# Coach MyTalleyrand (Python)

Application de coaching en temps réel pour Civilization V.

## Installation

### Option recommandée (depuis la racine du repo)

```bash
./scripts/install_macos.sh
```

### Option manuelle (développement)

```bash
cd coach
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

## Configuration LLM (clé + prompts)

Le coach lit la configuration non sensible depuis :

1. **Base projet** : `coach/config/settings.json`
2. **Utilisateur local** : `~/Library/Application Support/MyTalleyrand/coach.user.json`

La clé OpenAI est lue en priorité depuis `TALLEYRAND_OPENAI_API_KEY`, puis depuis le Keychain macOS (`MyTalleyrand` / `openai`).

Un exemple est fourni dans `coach/config/coach.user.example.json`. Les constantes de `src.config` font foi ; régénérez l'exemple avec `python3 coach/scripts/generate_user_example.py` depuis la racine du dépôt.

Gestion manuelle de la clé sans relancer l'installateur :

```bash
cd coach
python3 -m src.keychain set openai
python3 -m src.keychain get openai
python3 -m src.keychain delete openai
```

### Champs configurables

- `coach.analysis_interval_turns` : fréquence des analyses LLM (10 par défaut ; 20 réduit environ de moitié les appels face à 10).
- `coach.detail_level` : `brief`, `standard` ou `detailed`; `brief` limite la verbosité et plafonne la sortie à 250 tokens, `detailed` autorise jusqu’à 700 tokens.
- `coach.cost_limit_usd` : plafond indicatif affiché dans l’overlay (2.0 USD par défaut; à comparer au jalon produit exprimé en euros comme ordre de grandeur).
- `llm.system_prompt` : prompt système complet.
- `llm.user_prompt_template` : template prompt utilisateur (doit contenir `{victory_focus}` et `{game_state_json}`).

> Priorité des variables d'environnement :
> `TALLEYRAND_OPENAI_API_KEY`, `TALLEYRAND_LLM_SYSTEM_PROMPT`, `TALLEYRAND_LLM_USER_PROMPT_TEMPLATE`, `TALLEYRAND_ANALYSIS_INTERVAL_TURNS`, `TALLEYRAND_LLM_DETAIL_LEVEL`, `TALLEYRAND_COST_LIMIT_USD`.

## Overlay

Après chaque conseil, l’overlay affiche le coût LLM cumulé estimé de la partie en cours et ajoute un marqueur ⚠️ quand 80% du plafond configuré est atteint. Le calcul utilise les tokens retournés par le provider et des tarifs indicatifs en USD; il sert au pilotage en jeu, pas à remplacer la facturation fournisseur.

L'overlay utilise la police `Inter` si elle est installée sur macOS, puis bascule automatiquement sur Helvetica/Arial/sans-serif. `Inter` n'est pas embarquée : c'est une préférence visuelle optionnelle, pas une dépendance obligatoire.

## Lancement

```bash
cd coach
python3 src/main.py
```

Les réglages budget (`analysis_interval_turns`, `detail_level`, `cost_limit_usd`) sont relus entre deux tours si `settings.json` ou `coach.user.json` change : une partie en cours peut donc passer de 10 à 20 tours d’intervalle sans redémarrer. Le bouton ⚙ de l’overlay permet de changer de stratégie de victoire en cours de partie ; le choix est sauvegardé dans `user_preferences.json` dans le dossier export du mod et repris dès l’analyse suivante. Au tour 1, l’overlay demande ce choix une seule fois en mode PyQt6.

Mode one-shot (smoke test) :

```bash
python3 src/main.py --once --victory-focus science
```

## Échange de données mod ↔ coach

- Fichier attendu : `.../MODS/MyTalleyrand/export/gamestate.json`
- Schéma validé : `coach/config/gamestate.schema.v0.json`
- Champs minimum : `schema_version`, `turn_id`, `turn_number`, `timestamp_utc`, `player`, `resources`
- Champs optionnels utilisés par la logique coach : `game`/`settings`/`game_parameters` pour difficulté, taille de carte et vitesse ; `cities`/`units` pour éviter les conseils trop certains quand le contexte est pauvre.
- Déduplication par `turn_id`
- Fréquence de refresh watcher : `0.5s`

## Tests

```bash
./scripts/test.sh
./scripts/lint.sh
python3 -m pytest
```
