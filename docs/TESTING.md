# Tests — MyTalleyrand

## Tests automatisés (coach Python)

```bash
cd coach && python3 -m pytest
```

| Fichier | Couvre |
|---------|--------|
| `test_config.py` | Configuration multi-niveaux, surcharges env, résolution Keychain |
| `test_keychain.py` | Adaptateur Keychain/keyring et fallbacks sûrs |
| `test_llm_client.py` | Client LLM, fallback local, parsing strict |
| `test_watcher.py` | Surveillance fichier, déduplication turn_id, notifications gamestate invalide |
| `test_coach_engine.py` | Déclenchement tour 1 + tous les 10 tours, historique, résilience JSON corrompu |
| `test_pipeline_integration.py` | Chaîne watcher → coach → overlay |
| `test_overlay.py` | Position, visibilité, rendu texte, statut utilisateur, résilience état corrompu |
| `test_gamestate_schema.py` | Validation champs requis et types |

### Smoke test (premier lancement)

```bash
cd coach && ./scripts/first_test.sh
```

Crée un `gamestate.json` minimal, lance le coach en mode `--once`, vérifie la génération de `coach_history.json`.

## Validation complète du projet

```bash
./scripts/validate.sh
```

Vérifie : présence des fichiers clés, syntaxe XML (`xmllint`), tests Python (`pytest`).

## Validation XML du mod

```bash
xmllint --noout mod/MyTalleyrand.modinfo mod/XML/GameDefines.xml mod/XML/Text.xml
```

## Tests manuels (avec Civilization V)

### Installation du mod

```bash
# Via script automatisé
./scripts/install_macos.sh

# Ou manuellement
cp -R mod/. ~/Documents/Aspyr/Sid\ Meier\'s\ Civilization\ 5/MODS/MyTalleyrand/
mkdir -p ~/Documents/Aspyr/Sid\ Meier\'s\ Civilization\ 5/MODS/MyTalleyrand/export
```

### Procédure de test

1. Lancer Civ5 → menu MODS → activer MyTalleyrand
2. Démarrer une partie (Duel, Quick)
3. Vérifier la génération de `export/gamestate.json` après le premier tour
4. Lancer le coach : `cd coach && python3 src/main.py --once --victory-focus science`
5. Vérifier les logs : `tail -f ~/talleyrand.log`

### Logs Civ5 (macOS)

```
~/Documents/Aspyr/Sid Meier's Civilization 5/Logs/Database.log
~/Documents/Aspyr/Sid Meier's Civilization 5/Logs/Lua.log
```

### Troubleshooting

| Problème | Solution |
|----------|----------|
| Mod absent du menu MODS | Vérifier que `.modinfo` est dans le dossier MODS |
| Crash au chargement | Consulter `Database.log` et `Lua.log` |
| `gamestate.json` non généré | Vérifier permissions du dossier `export/` |
| Overlay ne s'affiche pas | Civ5 doit être en mode fenêtré |

## Checklist avant commit

- [ ] `./scripts/validate.sh` passe
- [ ] Pas de fichier > 500 lignes
- [ ] Pas de code mort
- [ ] Documentation à jour
