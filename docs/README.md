# Documentation MyTalleyrand

Index des documents projet.

## Documents essentiels

- `QUICKSTART.md` : démarrage rapide.
- `MACOS_GUIDE.md` : guide technique macOS (overlay, permissions).
- `TESTING.md` : stratégie et commandes de test.
- `DEVELOPMENT_PLAN.md` : séquencement des phases.
- `BACKLOG.md` : user stories et roadmap.

## État actuel

- Pipeline mod → coach validé.
- Schéma gamestate `0.1.0` utilisé côté mod et coach.
- Installation macOS simplifiée via `../script/install_macos.sh`.
- Configuration utilisateur LLM externalisée dans `~/Library/Application Support/MyTalleyrand/coach.user.json`.

## Parcours recommandé

1. Lire `../README.md`.
2. Exécuter `../script/install_macos.sh`.
3. Vérifier la config utilisateur LLM.
4. Lancer les tests (`../scripts/validate.sh`).
