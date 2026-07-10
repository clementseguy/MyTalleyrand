# MyTalleyrand

Mod Civilization V + coach Python (LLM) pour proposer des recommandations stratégiques en jeu.

> **Vous débutez en informatique ?** Pas de panique. Le guide ci-dessous vous prend par la main, étape par étape. Vous n'avez rien à « coder » : vous copiez-collez quelques lignes et le programme fait le reste.

## Installation guidée (macOS, pour débutants)

### Ce dont vous avez besoin avant de commencer

| Prérequis | Comment vérifier / obtenir |
|-----------|-----------------------------|
| **macOS** | Vous êtes sur un Mac (c'est la seule plateforme supportée pour l'instant). |
| **Civilization V** | Le jeu doit être installé (version Steam ou Aspyr). Lancez-le au moins une fois avant de continuer. |
| **Python 3** | L'installateur vérifie automatiquement sa présence et vous guide s'il manque. |
| **Une clé Mistral** (recommandé) ou OpenAI | Elle permet au coach de donner des conseils « intelligents ». Mistral est le provider par défaut ; OpenAI reste disponible par configuration. Sans clé, le coach fonctionne quand même en mode local simplifié. |

> 💡 Les providers LLM sont **payants à l'usage** (quelques centimes par partie en général), mais l'obtention d'une clé est gratuite. Vous gardez le contrôle du budget.

### Étape 1 — Télécharger le projet

Deux possibilités :

- **Le plus simple :** sur la page GitHub du projet, cliquez sur le bouton vert **`Code`** puis **`Download ZIP`**. Ouvrez ensuite le fichier `.zip` téléchargé (dans votre dossier `Téléchargements`) : un dossier `MyTalleyrand-...` apparaît.
- **Si vous connaissez Git :**

  ```bash
  git clone https://github.com/<votre-compte>/MyTalleyrand.git
  ```

### Étape 2 — Ouvrir le Terminal

Le Terminal est l'application qui permet de lancer l'installateur.

1. Appuyez sur **`Cmd (⌘) + Espace`** pour ouvrir Spotlight.
2. Tapez **`Terminal`** puis appuyez sur **`Entrée`**.
3. Une fenêtre avec du texte s'ouvre : c'est là que vous collerez les commandes.

### Étape 3 — Aller dans le dossier du projet

Dans le Terminal, tapez `cd ` (avec un espace après), **sans appuyer sur Entrée tout de suite**, puis **glissez-déposez le dossier `MyTalleyrand`** (celui décompressé à l'étape 1) directement dans la fenêtre du Terminal. Son chemin s'écrit tout seul. Appuyez ensuite sur **`Entrée`**.

Exemple de ce que ça donne :

```bash
cd /Users/vous/Downloads/MyTalleyrand
```

### Étape 4 — Lancer l'installation

Copiez-collez cette ligne dans le Terminal, puis appuyez sur **`Entrée`** :

```bash
./scripts/install_macos.sh
```

L'installateur vous accompagne : il vérifie les prérequis, installe le mod et le coach, puis vous **demande votre clé Mistral** par défaut. Laissez-vous guider par les messages à l'écran.

> Si macOS refuse de lancer le script (« autorisation refusée »), tapez d'abord :
> ```bash
> chmod +x ./scripts/install_macos.sh
> ```
> puis relancez la commande de l'étape 4.

### Étape 5 — Lancer le coach

Une fois l'installation terminée, ouvrez le **Finder**, allez dans **Applications → MyTalleyrandCoach**, et **double-cliquez** sur **`start_coach.command`**.

Ou, depuis le Terminal :

```bash
open ~/Applications/MyTalleyrandCoach/start_coach.command
```

> La première fois, macOS peut afficher un avertissement de sécurité. Faites un **clic droit** sur `start_coach.command` → **Ouvrir** → **Ouvrir**, pour l'autoriser.

### Étape 6 — Lancer Civilization V

1. Démarrez **Civilization V**.
2. Dans le menu **Mods**, activez le mod **MyTalleyrand**.
3. Réglez le jeu en **mode fenêtré** (Options → Vidéo → Fenêtré ou Fenêtré plein écran) pour que les conseils du coach restent visibles au-dessus du jeu.
4. Lancez une partie : les conseils apparaissent automatiquement au fil des tours. 🎉

### En cas de souci

- Relancez un **diagnostic guidé** qui vérifie tout sans démarrer le coach :

  ```bash
  cd ~/Applications/MyTalleyrandCoach/coach
  .venv/bin/python src/main.py --onboarding
  ```

- Consultez le [Guide macOS](docs/MACOS_GUIDE.md) (permissions, dépannage, overlay invisible, etc.).

### Où sont mes réglages ?

- Fichier de configuration utilisateur : `~/Library/Application Support/MyTalleyrand/coach.user.json`
- Les clés Mistral/OpenAI sont stockées de façon sécurisée dans le **Trousseau (Keychain) macOS**, pas en clair dans un fichier.
- L'objectif de victoire est demandé au tour 1 dans l'overlay et modifiable ensuite avec le bouton ⚙ (sauvegardé dans `user_preferences.json`).

## Annexe — Choisir un provider LLM

Mistral est utilisé par défaut avec le modèle `mistral-small-latest`. Pour enregistrer une clé Mistral manuellement :

```bash
cd coach
python3 -m src.keychain set mistral
```

OpenAI reste disponible en configuration explicite :

```bash
TALLEYRAND_LLM_PROVIDER=openai python3 src/main.py
```

ou dans `~/Library/Application Support/MyTalleyrand/coach.user.json` :

```json
{
  "llm": {
    "provider": "openai"
  }
}
```

## Annexe — Créer une clé OpenAI (pas à pas)

La clé OpenAI donne au coach l'accès à un modèle d'IA pour analyser vos parties. Voici comment l'obtenir :

1. **Créer un compte** sur <https://platform.openai.com/signup> (ou se connecter si vous en avez déjà un).
2. **Ajouter un moyen de paiement et un crédit** : allez dans **Settings → Billing** (<https://platform.openai.com/settings/organization/billing/overview>). Ajoutez une carte, puis un petit crédit (par exemple 5 $) suffit largement pour de nombreuses parties.
3. **Générer la clé** : ouvrez <https://platform.openai.com/api-keys>, cliquez sur **`Create new secret key`**, donnez-lui un nom (ex. « MyTalleyrand »), puis **`Create secret key`**.
4. **Copier la clé immédiatement** : elle commence par `sk-...` et **ne s'affiche qu'une seule fois**. Copiez-la (bouton de copie) et gardez-la de côté un instant.
5. **La coller dans l'installateur** : quand le script vous demande la clé (étape 4 ci-dessus), collez-la avec `Cmd (⌘) + V` puis `Entrée`. Elle n'apparaît pas à l'écran pendant la saisie : c'est normal, c'est pour la sécurité.

> 🔒 **Ne partagez jamais votre clé.** Elle est personnelle et liée à votre facturation OpenAI. Si vous pensez l'avoir divulguée, révoquez-la depuis la page **API keys** et créez-en une nouvelle.
>
> 💰 **Maîtriser le budget :** dans **Billing**, vous pouvez fixer une **limite de dépense** (« usage limits »). Le coach affiche aussi une estimation du coût cumulé pendant la partie.

Vous n'avez pas de clé ou préférez ne pas en créer ? L'installateur vous laisse simplement appuyer sur `Entrée` : le coach fonctionnera alors en **mode local simplifié**, sans IA en ligne.

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
└── scripts/                     # scripts de validation/dev
```

## Architecture (simplifiée)

- **mod/** : à chaque tour du joueur actif, écrit l'état de partie (JSON) dans sa base `ModUserData` (SQLite) — sur macOS le Lua ne peut pas écrire de fichier directement.
- **coach/** : surveille cette source (`poll_interval=0.5s`), valide le schéma, détecte les paramètres de partie disponibles, puis génère un conseil (LLM, fallback local ou avertissement de contexte insuffisant).
- **overlay** : fenêtre PyQt6 transparente et persistante qui affiche l'objectif à 10 tours, les actions prioritaires, les risques et les statuts utilisateur.

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

- ✅ Chaîne mod → watcher → coach → overlay PyQt6 opérationnelle en mode fenêtré.
- ✅ Fallback local robuste si LLM indisponible.
- ✅ Configuration utilisateur LLM (clé + prompts) via fichier dédié.
- ⚠️ Support principal : macOS (Aspyr/Steam).

## Fonctionnalités prévues (simplifié)

- Packaging applicatif macOS (app bundle/signature).
- Amélioration du schéma de gamestate (économie, villes, diplomatie détaillées).
- Ajout d'options UI overlay (thèmes, filtres de catégories, raccourcis clavier).

## Désinstallation

```bash
./scripts/uninstall_macos.sh
# Optionnel : supprimer aussi la config utilisateur et les logs
REMOVE_USER_DATA=1 REMOVE_LOGS=1 ./scripts/uninstall_macos.sh
```

Le script supprime le coach installé, le mod installé et tente de révoquer les clés Mistral/OpenAI stockées dans le Keychain macOS.

## Documentation

- [Documentation technique](docs/README.md) — architecture, config, conventions
- [Backlog v0.1](docs/BACKLOG_v0.1.md) — backlog initial
- [Backlog v0.2](docs/BACKLOG_v0.2.md) — nouvelles tâches debug, recette, Mistral et maintenance
- [Backlog v0.3](docs/BACKLOG_v0.3.md) — préparation du partage communauté
- [Tests](docs/TESTING.md) — tests automatisés et manuels
- [Guide macOS](docs/MACOS_GUIDE.md) — chemins, permissions, packaging
- [README Coach](coach/README.md)
- [README Mod](mod/README.md)

## Licence

Ce projet est distribué sous licence **MIT**.

Voir le fichier [`LICENSE`](LICENSE).

## Avertissement de responsabilité

Ce mod et ce coach sont fournis **en l'état**, sans garantie.

L'utilisation de MyTalleyrand est sous l'entière responsabilité des personnes qui choisissent de l'utiliser. L'auteur ne pourra pas être tenu responsable de tout dommage, perte de données, suspension de compte, ou tout autre impact direct ou indirect lié à l'utilisation du projet.
