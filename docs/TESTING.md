# Tests — MyTalleyrand

## Tests automatisés (coach Python)

```bash
cd coach && python3 -m pytest
```

| Fichier | Couvre |
|---------|--------|
| `test_config.py` | Configuration multi-niveaux, surcharges env, résolution Keychain |
| `test_keychain.py` | Adaptateur Keychain/keyring et fallbacks sûrs |
| `test_llm_client.py` | Client LLM, retry réseau avec statut UX, fallback local, parsing strict |
| `test_watcher.py` | Surveillance fichier, déduplication turn_id, notifications gamestate invalide |
| `test_coach_engine.py` | Déclenchement tour 1 + tous les 10 tours, historique, résilience JSON corrompu |
| `test_pipeline_integration.py` | Chaîne watcher → coach → overlay |
| `test_overlay.py` | Position, visibilité, rendu texte, statut utilisateur, résilience état corrompu |
| `test_gamestate_schema.py` | Validation champs requis et types |
| `test_onboarding.py` | Vérifications premier lancement et marqueur `.onboarding_done` |
| `test_main_cli.py` | Surcharges CLI debug/interval/provider sans lancer le watcher |

### Smoke test (premier lancement)

```bash
cd coach && ./scripts/first_test.sh
```

Crée un `gamestate.json` minimal en mode `TALLEYRAND_GAMESTATE_SOURCE=file`, lance le coach en mode `--once`, vérifie la génération de `coach_history.json`. Ce smoke test ne remplace pas la recette macOS nominale SQLite.

## Validation complète du projet

```bash
./scripts/validate.sh
```

Vérifie : présence des fichiers clés, syntaxe XML (`xmllint`), tests Python (`pytest`).

## Validation XML du mod

```bash
xmllint --noout mod/MyTalleyrand.modinfo mod/XML/GameDefines.xml mod/XML/Text.xml
```

## Recette R0 en moins de 15 minutes

### 1. Préparer Civ5 et le coach du dépôt

```bash
./scripts/enable_debug.sh
./scripts/run_coach.sh --debug
```

`--debug` force `analysis_interval_turns=1` et active des logs plus verbeux. Équivalents :

```bash
./scripts/run_coach.sh --interval 1
TALLEYRAND_ANALYSIS_INTERVAL_TURNS=1 ./scripts/run_coach.sh
```

### 2. Valider la source SQLite ModUserData

Lancez Civilization V en mode fenêtré, activez le mod depuis le menu Mods, jouez un tour, puis vérifiez :

```bash
CIV="$HOME/Library/Application Support/Sid Meier's Civilization 5"
sqlite3 "$CIV/ModUserData/a1b2c3d4-e5f6-7890-abcd-ef1234567890-1.db" \
  "SELECT Name FROM SimpleValues WHERE Name='gamestate_json';"
tail -f ~/talleyrand.log
```

Le flux nominal macOS est SQLite `ModUserData`; `gamestate.json` n'est pas attendu en recette macOS.

### 3. Valider overlay fermer/réduire

1. Attendez un conseil affiché dans l'overlay.
2. Cliquez `–` : l'overlay reste visible mais réduit ; le prochain conseil le déplie.
3. Cliquez `×` : l'overlay est masqué ; le prochain conseil le réaffiche automatiquement.
4. Gardez Civ5 en mode fenêtré ou fenêtré plein écran.

### 4. Valider providers LLM

Mistral est le provider par défaut :

```bash
./scripts/run_coach.sh --debug --llm-provider mistral
```

OpenAI reste disponible :

```bash
./scripts/run_coach.sh --debug --llm-provider openai
```

Pour tester les messages actionnables, lancez avec une clé invalide ou sans crédit. Les erreurs clé invalide/quota doivent apparaître immédiatement sans trois retries ; une panne réseau transitoire déclenche des statuts `Reconnexion LLM en cours` puis un fallback local.

## Tests manuels (avec Civilization V)

### Installation du mod

```bash
# Via script automatisé
./scripts/install_macos.sh

# Ou manuellement, uniquement dans le dossier Library supporté
CIV="$HOME/Library/Application Support/Sid Meier's Civilization 5"
mkdir -p "$CIV/MODS/MyTalleyrand"
cp -R mod/. "$CIV/MODS/MyTalleyrand/"
```

### Procédure de test

1. Lancer Civ5 → menu MODS → activer MyTalleyrand
2. Démarrer une partie (Duel, Quick)
3. Vérifier la présence de `gamestate_json` dans SQLite `ModUserData` après le premier tour
4. Lancer le coach : `./scripts/run_coach.sh --debug --victory-focus science`
5. Vérifier les logs : `tail -f ~/talleyrand.log`

### Logs Civ5 (macOS)

```
~/Library/Application Support/Sid Meier's Civilization 5/Logs/Database.log
~/Library/Application Support/Sid Meier's Civilization 5/Logs/Lua.log
```

### Troubleshooting

| Problème | Solution |
|----------|----------|
| Mod absent du menu MODS | Vérifier que `.modinfo` est dans le dossier MODS |
| Crash au chargement | Consulter `Database.log` et `Lua.log` |
| SQLite `ModUserData` vide | Vérifier que la partie est lancée depuis le menu Mods et consulter `Lua.log` |
| Overlay ne s'affiche pas | Civ5 doit être en mode fenêtré ; le prochain conseil réaffiche l'overlay fermé |
| Erreur clé/quota LLM | Vérifier Keychain `python3 -m src.keychain set mistral` ou `openai`, ou ajouter du crédit provider |

## Checklist avant commit

- [ ] `./scripts/validate.sh` passe
- [ ] Pas de fichier > 500 lignes
- [ ] Pas de code mort
- [ ] Documentation à jour
