# MyTalleyrand

Mod Civilization V + coach Python (LLM) pour proposer des recommandations stratégiques en jeu.

## Démarrage rapide (macOS)

1. **Installer automatiquement mod + coach**

```bash
./script/install_macos.sh
```

2. **Vérifier la configuration coach**
- Fichier utilisateur : `~/Library/Application Support/MyTalleyrand/coach.user.json`
- Champs clés à renseigner :
  - `llm.api_key`
  - `llm.system_prompt` (facultatif, personnalisable)
  - `llm.user_prompt_template` (facultatif, doit contenir `{victory_focus}` et `{game_state_json}`)

3. **Lancer le coach**

```bash
cd ~/Applications/MyTalleyrandCoach/coach
.venv/bin/python src/main.py
```

4. **Lancer Civilization V**
- Activer le mod **MyTalleyrand** dans le menu Mods.
- Jouer en mode fenêtré.

## Structure actuelle du projet

```text
MyTalleyrand/
├── coach/
│   ├── config/                  # settings + schéma + exemple config utilisateur
│   ├── src/                     # watcher, moteur de coach, client LLM, overlay
│   ├── tests/                   # tests unitaires/intégration
│   └── README.md
├── docs/                        # documentation technique/projet
├── mod/                         # mod Civilization V (Lua/XML/SQL)
├── script/                      # scripts d'installation utilisateur
└── scripts/                     # scripts de validation/dev
```

## Architecture (simplifiée)

- **mod/** : exporte `gamestate.json` à chaque tour joueur actif.
- **coach/** : surveille ce fichier (`poll_interval=0.5s`), valide le schéma, puis génère un conseil (LLM ou fallback local).
- **overlay** : affiche l'objectif à 10 tours, actions prioritaires, risques et catégories.

## Développement (simplifié)

- Validation rapide :

```bash
./scripts/validate.sh
```

- Tests coach :

```bash
cd coach
python3 -m pytest
```

## Statut du projet (simplifié)

- ✅ Chaîne mod → watcher → coach → overlay opérationnelle.
- ✅ Fallback local robuste si LLM indisponible.
- ✅ Configuration utilisateur LLM (clé + prompts) via fichier dédié.
- ⚠️ Support principal : macOS (Aspyr/Steam).

## Fonctionnalités prévues (simplifié)

- Packaging applicatif macOS (app bundle/signature).
- Amélioration du schéma de gamestate (économie, villes, diplomatie détaillées).
- Ajout d'options UI overlay (thèmes, filtres de catégories, raccourcis clavier).

## Documentation

- [README Coach](coach/README.md)
- [README Mod](mod/README.md)
- [Index docs](docs/README.md)

## Licence

Ce projet est distribué sous licence **MIT**.

Voir le fichier [`LICENSE`](LICENSE).

## Avertissement de responsabilité

Ce mod et ce coach sont fournis **en l'état**, sans garantie.

L'utilisation de MyTalleyrand est sous l'entière responsabilité des personnes qui choisissent de l'utiliser. L'auteur ne pourra pas être tenu responsable de tout dommage, perte de données, suspension de compte, ou tout autre impact direct ou indirect lié à l'utilisation du projet.
