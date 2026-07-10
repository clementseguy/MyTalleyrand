# BACKLOG MyTalleyrand v0.2

**Date de mise à jour :** 10 juillet 2026
**Version :** 0.2
**Sprint actuel :** Sprint R0 - Debug & recette jouable

> **Contexte du projet :** ce backlog v0.2 complète le backlog initial conservé dans `docs/BACKLOG_v0.1.md`. Il ne reprend pas toutes les US déjà planifiées/terminées en v0.1 : il organise les nouvelles tâches issues de `TODO.md`, avec une priorité explicite sur le debug, la recette et l'intégration de Mistral.

---

## Définitions de succès (jalons)

Trois jalons pilotent cette v0.2 :

| Jalon | Définition | Portée |
| --- | --- | --- |
| **Recette debug** | Je peux lancer le coach depuis le dépôt, forcer l'analyse à chaque tour, diagnostiquer les erreurs et vérifier l'overlay sans jouer 10-20 tours entre deux tests. | Sprint R0 |
| **Mistral opérationnel** | Mistral est disponible comme provider par défaut, avec une robustesse comparable à OpenAI : configuration, logs, erreurs actionnables, fallback local. | Sprint R0 |
| **MVP jouable robuste** | Une partie réelle peut être jouée avec des conseils utiles dès le tour 1, sans blocage overlay/LLM, et avec une base technique maintenable. | Sprints R0-R1 |

**Contraintes actées :**
- Plateforme : **macOS uniquement** pour cette phase.
- Civ5 Steam/macOS tourne en environnement Windows émulé : le mod ne peut pas écrire de fichier (`io`/`os` indisponibles).
- Source de vérité gamestate : base SQLite **`ModUserData`**, contenant un payload JSON lu par le coach.
- Priorité n°1 : **faciliter le debug et la recette de MyTalleyrand**, y compris l'utilisation de Mistral.
- Qualité : la v0.2 doit réduire la dette technique pour faciliter maintenance, évolution des providers LLM et enrichissement du gamestate.

---

## Vue d'ensemble

| Métrique | Valeur |
| --- | --- |
| **Total User Stories** | 20 |
| **US Terminées** | 0 |
| **US En cours (partielles)** | 0 |
| **US À faire** | 20 |
| **US Won't** | 0 |
| **Progression** | 0/20 actives — 0% |

### Répartition par Epic

| Epic | US | Jalon dominant | Statut |
| --- | --- | --- | --- |
| EPIC 0 : Debug, recette & stabilisation | 9 | Recette debug / Mistral | 📝 0/9 terminées |
| EPIC 2 : Qualité de code & évolutivité | 5 | Maintenance | 📝 0/5 terminées |
| EPIC 1 : Qualité des conseils & aide en jeu | 4 | MVP jouable robuste | 📝 0/4 terminées |
| EPIC 3 : Budget & consommation API | 2 | Maîtrise budget | 📝 0/2 terminées |

### Légende des statuts

- 📝 **À faire** · 🔄 **En cours** · ✅ **Terminé** · ⏸️ **En attente** · 🚫 **Abandonné**

### Légende MoSCoW

- 🔴 **Must** (bloquant pour un jalon) · 🟠 **Should** (fort impact, non bloquant) · 🟢 **Could** (confort) · ⚪ **Won't** (hors périmètre pour ce cycle)

---

## EPIC 0 : Debug, recette & stabilisation

**Objectif :** Rendre MyTalleyrand facile à lancer, diagnostiquer et valider pendant une vraie partie, avec Mistral comme provider LLM par défaut.
**Statut global :** 📝 0/9 terminées
**Priorité :** priorité n°1 actuelle ; **US-030 est la priorité n°1 de cet Epic**.

---

### US-030 : Intégration Mistral comme provider par défaut

**Statut :** 📝 À faire · **Priorité :** 🔴 Must · **Jalon :** Mistral opérationnel · **Sprint :** Sprint R0

**User Story :**
> En tant qu'**utilisateur**, je veux **choisir Mistral ou OpenAI au lancement du coach, avec Mistral par défaut**, afin de **recetter MyTalleyrand avec le provider cible tout en gardant un fallback connu**.

#### Tâches techniques
- Étendre `coach/src/llm_client.py` avec un client Mistral robuste : configuration, modèle par défaut, timeouts, retries, erreurs non retryables.
- Ajouter le choix de provider au lancement/onboarding et dans la config (`mistral` par défaut, `openai` disponible).
- Stocker les clés API via Keychain avec services/comptes distincts (`MyTalleyrand/mistral`, `MyTalleyrand/openai`).
- Harmoniser logs, parsing JSON, coût estimé et fallback local entre providers.
- Ajouter tests unitaires avec réponses simulées Mistral et OpenAI.

#### Critères d'acceptation
✅ Une nouvelle installation propose Mistral par défaut
✅ OpenAI reste utilisable par configuration explicite
✅ Les erreurs quota/auth/réseau sont distinguées pour les deux providers

#### Dépendances
- US-003, US-011b du backlog v0.1, US-024

---

### US-023 : Overlay restauré automatiquement à chaque nouveau conseil

**Statut :** 📝 À faire · **Priorité :** 🔴 Must · **Jalon :** Recette debug · **Sprint :** Sprint R0

**User Story :**
> En tant que **joueur**, je veux **que l'overlay réapparaisse automatiquement quand un nouveau conseil est disponible**, afin de **ne jamais manquer une analyse parce que j'ai fermé la fenêtre au tour précédent**.

#### Contexte debug
- `TalleyrandOverlay.hide()` persiste `visible=false` dans `export/overlay_state.json`.
- `show_advice()` remet `minimized=false`, mais ne force pas `visible=true`.
- Résultat observé : overlay visible au tour 1, fermé avec `×`, puis invisible au tour 10.

#### Tâches techniques
- Modifier `coach/src/overlay.py` pour que `show_advice()` force `visible=true` sur un nouveau conseil.
- Clarifier la sémantique UX entre **réduire** (`-`) et **masquer/fermer** (`×`).
- Vérifier le placement multi-écrans et documenter que Civ5 doit rester en mode fenêtré.
- Ajouter un test de régression : `hide()` puis nouveau `show_advice()` rend l'overlay visible.

#### Critères d'acceptation
✅ Après fermeture avec `×`, le conseil suivant réaffiche l'overlay sans supprimer manuellement `overlay_state.json`
✅ Le comportement réduire/fermer est compréhensible et testé

#### Dépendances
- US-004, US-017 du backlog v0.1

---

### US-024 : Erreurs LLM non retryables et messages actionnables

**Statut :** 📝 À faire · **Priorité :** 🔴 Must · **Jalon :** Recette debug · **Sprint :** Sprint R0

**User Story :**
> En tant qu'**utilisateur**, je veux **voir immédiatement si ma clé API est invalide ou mon crédit est épuisé**, afin de **corriger la configuration sans attendre des retries inutiles**.

#### Contexte debug
- Le cas OpenAI `429 insufficient_quota` est traité comme une erreur générique.
- Le coach effectue plusieurs retries inutiles avant fallback.

#### Tâches techniques
- Dans `coach/src/llm_client.py`, classer `401`, clé manquante/invalide et `insufficient_quota` comme erreurs non retryables.
- Afficher dans l'overlay un message distinct : crédit épuisé, clé invalide, panne réseau transitoire.
- Conserver les retries uniquement pour les timeouts, erreurs réseau et erreurs serveur retryables.
- Prévoir la même classification pour Mistral lors de l'US-030.
- Ajouter des tests sur la politique de retry et les statuts utilisateur.

#### Critères d'acceptation
✅ `insufficient_quota` et `401` ne déclenchent pas 3 tentatives
✅ L'utilisateur reçoit un message explicite et actionnable
✅ Le fallback local reste disponible sans masquer la cause réelle

#### Dépendances
- US-003, US-016 du backlog v0.1

---

### US-026 : Mode debug tour par tour

**Statut :** 📝 À faire · **Priorité :** 🔴 Must · **Jalon :** Recette debug · **Sprint :** Sprint R0

**User Story :**
> En tant que **développeur en recette**, je veux **forcer une analyse à chaque tour depuis la CLI**, afin de **tester le pipeline sans jouer 10 à 20 tours entre deux observations**.

#### Tâches techniques
- Ajouter `--debug` et/ou `--interval N` à `coach/src/main.py`.
- Faire de `--debug` un raccourci pour `analysis_interval_turns=1` + logs plus verbeux.
- Documenter l'équivalent env `TALLEYRAND_ANALYSIS_INTERVAL_TURNS=1`.
- Tester que les flags CLI surchargent proprement la config.

#### Critères d'acceptation
✅ `python src/main.py --debug` analyse chaque tour
✅ `python src/main.py --interval 1` fonctionne sans modifier `settings.json`

#### Dépendances
- US-007, US-011 du backlog v0.1

---

### US-027 : Script de run développement

**Statut :** 📝 À faire · **Priorité :** 🔴 Must · **Jalon :** Recette debug · **Sprint :** Sprint R0

**User Story :**
> En tant que **développeur**, je veux **lancer le coach depuis le dépôt de travail avec le bon environnement Python**, afin de **recetter mes changements sans utiliser une copie installée obsolète**.

#### Tâches techniques
- Ajouter ou consolider `scripts/run_coach.sh` / `.command` pour lancer `coach/src/main.py` depuis le dépôt.
- Vérifier les scripts existants : `scripts/start_coach.command`, `scripts/start.sh`, `coach/scripts/run.sh`.
- Prévoir une variante debug ou un passage transparent des arguments (`"$@"`).
- Échouer avec un message clair si `.venv` est absent ou cassé.

#### Critères d'acceptation
✅ Une commande documentée lance le coach du dépôt courant
✅ Les arguments `--debug` / `--interval` sont transmis
✅ Le script n'utilise pas la copie installée dans `~/Applications`

#### Dépendances
- US-002 du backlog v0.1, US-026

---

### US-028 : Installation macOS alignée sur SQLite ModUserData

**Statut :** 📝 À faire · **Priorité :** 🔴 Must · **Jalon :** Recette debug · **Sprint :** Sprint R0

**User Story :**
> En tant qu'**utilisateur macOS**, je veux **un script d'installation cohérent avec l'architecture réelle**, afin de **ne pas créer de conflit de mod ni de dépendance à un dossier d'export inexistant**.

#### Contexte debug
- Installer le mod dans Library et Aspyr peut causer `UNIQUE constraint failed: ModFiles`.
- Le mod publie désormais l'état dans SQLite `ModUserData`, pas dans un dossier `export/`.
- Un `.venv` livré ou recréé sous un autre utilisateur peut être cassé.

#### Tâches techniques
- Modifier `scripts/install_macos.sh` pour installer uniquement dans `~/Library/Application Support/Sid Meier's Civilization 5/MODS/`.
- Retirer les étapes obsolètes liées au dossier `export/`.
- Recréer proprement le venv local plutôt que réutiliser un environnement potentiellement non portable.
- Ajouter une option ou un script séparé `scripts/enable_debug.sh` pour flags Civ5 debug + purge cache mods.

#### Critères d'acceptation
✅ Une installation propre ne déclenche pas de doublon `ModFiles`
✅ Le coach sait lire la base `ModUserData` attendue
✅ La procédure de debug macOS est reproductible

#### Dépendances
- US-001, US-002, US-015 du backlog v0.1

---

### US-029 : Documentation de recette et troubleshooting post-debug

**Statut :** 📝 À faire · **Priorité :** 🟠 Should · **Jalon :** Recette debug / Partage public · **Sprint :** Sprint R0

**User Story :**
> En tant que **développeur ou testeur**, je veux **une procédure de recette courte et à jour**, afin de **valider overlay, SQLite, provider LLM et mode debug sans relire toute l'architecture**.

#### Tâches techniques
- Mettre à jour `docs/TESTING.md` avec scénarios manuels : overlay fermé puis nouveau conseil, tour 1, LLM quota/key invalid, Mistral, analyse interval=1.
- Mettre à jour `docs/MACOS_GUIDE.md` : chemins Civ5, cache mods, `config.ini` read-only si nécessaire, base SQLite réelle.
- Mettre à jour README/docs fonctionnelles : ce que voit l'utilisateur, cadence, fallback local, modes local vs LLM.
- Documenter le contournement temporaire `overlay_state.json` seulement tant que US-023 n'est pas livrée.

#### Critères d'acceptation
✅ Une recette en moins de 15 minutes permet de valider les flux critiques
✅ Les docs ne mentionnent plus l'ancien export fichier comme chemin nominal

#### Dépendances
- US-023 à US-028, US-030

---

### US-037 : Audit et conservation temporaire du `.venv` de debug

**Statut :** 📝 À faire · **Priorité :** 🟠 Should · **Jalon :** Recette debug · **Sprint :** Sprint R0

**User Story :**
> En tant que **développeur**, je veux **conserver le `.venv` issu de la dernière séance de debug tout en vérifiant qu'il ne contient pas de secret**, afin de **ne pas perdre un environnement fonctionnel avant la prochaine séance de nettoyage**.

#### Contexte
- Le `.venv` a été largement modifié pendant une séance de debug.
- Il ne doit pas être supprimé immédiatement pour éviter de perdre du temps de remise en état.
- Il devra être nettoyé ou sorti du versionnement lors d'une prochaine séance dédiée.

#### Tâches techniques
- Scanner `.venv` pour détecter clés API, tokens, credentials ou chemins sensibles anormaux.
- Supprimer uniquement les secrets avérés si le scan en trouve, sans reconstruire l'environnement.
- Documenter l'état du `.venv` et la décision temporaire de conservation.
- Préparer une tâche future de nettoyage : `.gitignore`, recréation reproductible, suppression du suivi Git si validé.

#### Critères d'acceptation
✅ Aucun secret détectable n'est conservé dans `.venv`
✅ Le `.venv` reste utilisable pour la prochaine séance de debug
✅ La stratégie de nettoyage futur est documentée

#### Dépendances
- Aucune

---

### US-038 : Replay de recette depuis fixtures SQLite

**Statut :** 📝 À faire · **Priorité :** 🟠 Should · **Jalon :** Recette debug · **Sprint :** Sprint R1

**User Story :**
> En tant que **développeur en recette**, je veux **rejouer une séquence de tours depuis des fixtures SQLite**, afin de **tester le coach, l'overlay et les providers sans lancer Civilization V**.

#### Tâches techniques
- Créer des fixtures SQLite ou JSON représentatives : tour 1, tour 10, données pauvres, données enrichies, risque critique.
- Ajouter un mode CLI `--replay-fixture` ou équivalent.
- Vérifier que cache, coûts, overlay et fallback se comportent comme en partie réelle.
- Ajouter une documentation courte de recette sans Civ5.

#### Critères d'acceptation
✅ Une séquence de tours peut être rejouée localement sans Civ5
✅ Les scénarios overlay/LLM/gamestate sont testables de façon répétable

#### Dépendances
- US-027, US-034

---

## EPIC 2 : Qualité de code & évolutivité

**Objectif :** Réduire la dette technique issue du prototypage et faciliter les prochaines évolutions : providers LLM, schémas de gamestate, diagnostics, tests de non-régression.
**Statut global :** 📝 0/5 terminées

---

### US-033 : Revue qualité et découplage des responsabilités

**Statut :** 📝 À faire · **Priorité :** 🔴 Must · **Jalon :** Maintenance / MVP jouable robuste · **Sprint :** Sprint R1

**User Story :**
> En tant que **mainteneur**, je veux **un découpage clair entre lecture gamestate, décision coach, providers LLM, overlay et configuration**, afin de **faire évoluer MyTalleyrand sans régressions difficiles à diagnostiquer**.

#### Tâches techniques
- Faire une revue ciblée de `coach/src/main.py`, `coach.py`, `llm_client.py`, `overlay.py`, `config.py`, `gamestate_source.py`, `watcher.py`.
- Extraire une interface provider LLM commune si l'intégration Mistral rend `llm_client.py` trop dense.
- Vérifier que la logique métier ne dépend pas directement de PyQt6 ni de chemins macOS.
- Identifier et supprimer les duplications de configuration, chemins et messages utilisateur.
- Ajouter des types/docstrings courts sur les contrats publics entre modules.

#### Critères d'acceptation
✅ Les tests existants restent verts après refactor
✅ Ajouter un provider LLM ou une nouvelle version de schéma ne nécessite pas de modifier la boucle principale
✅ Les chemins macOS et les détails UI restent confinés aux modules dédiés

#### Dépendances
- US-030, US-031

---

### US-034 : Observabilité de recette

**Statut :** 📝 À faire · **Priorité :** 🔴 Must · **Jalon :** Recette debug · **Sprint :** Sprint R1

**User Story :**
> En tant que **développeur en debug**, je veux **des logs et diagnostics structurés par tour**, afin de **comprendre rapidement pourquoi un conseil est absent, local, distant, caché ou en erreur**.

#### Tâches techniques
- Ajouter un identifiant de cycle d'analyse dans les logs : tour, source gamestate, provider, cache hit, fallback, overlay state.
- Ajouter une commande ou option `--diagnose` qui vérifie chemins Civ5, base SQLite, config, Keychain, provider et permissions overlay.
- Éviter les logs de secrets API et documenter les redactions.
- Ajouter des tests sur le diagnostic sans dépendre d'une vraie installation Civ5.

#### Critères d'acceptation
✅ Un bug de recette peut être trié depuis les logs sans lancer un debugger Python
✅ Les diagnostics distinguent clairement données absentes, provider indisponible, conseil ignoré et overlay masqué

#### Dépendances
- US-026, US-027, US-030

---

### US-035 : Suite de tests de non-régression recette

**Statut :** 📝 À faire · **Priorité :** 🟠 Should · **Jalon :** Maintenance / Partage public · **Sprint :** Sprint R1

**User Story :**
> En tant que **mainteneur**, je veux **une suite de tests couvrant les scénarios de recette critiques**, afin de **modifier le coach avec confiance après les corrections de debug**.

#### Tâches techniques
- Couvrir les scénarios US-023 à US-032 : overlay fermé, tour 1, erreurs auth/quota, provider Mistral, interval=1, gamestate enrichi, surveillance des risques.
- Ajouter des fixtures réalistes de gamestate SQLite/exporté pour plusieurs tours.
- Ajouter une commande unique de validation locale (`scripts/validate.sh` ou équivalent) qui lance lint + tests pertinents.
- Nettoyer le périmètre versionné du `.venv` si nécessaire et documenter la création d'environnement.

#### Critères d'acceptation
✅ Les scénarios de recette critiques sont automatisés quand c'est raisonnable
✅ La validation locale indique clairement ce qui a échoué et pourquoi
✅ Le dépôt ne dépend pas d'artefacts d'environnement non portables

#### Dépendances
- US-023 à US-034

---

### US-041 : Nettoyage du versionnement de l'environnement Python

**Statut :** 📝 À faire · **Priorité :** 🟠 Should · **Jalon :** Maintenance · **Sprint :** Sprint R2

**User Story :**
> En tant que **mainteneur**, je veux **sortir l'environnement Python local du flux normal de versionnement**, afin de **réduire le bruit Git et rendre le projet plus reproductible**.

#### Tâches techniques
- Décider si `coach/.venv` doit être conservé temporairement, ignoré, archivé ou retiré du suivi Git.
- Ajouter ou corriger `.gitignore` pour éviter les mutations accidentelles du venv.
- Documenter la création reproductible de l'environnement depuis `coach/requirements.txt`.
- Vérifier que les scripts de run/install recréent ou utilisent correctement le venv.

#### Critères d'acceptation
✅ Les changements de dépendances ne produisent plus des centaines de diffs dans `.venv`
✅ Le coach reste lançable après recréation propre de l'environnement

#### Dépendances
- US-037

---

### US-042 : CI minimale de validation

**Statut :** 📝 À faire · **Priorité :** 🟠 Should · **Jalon :** Maintenance / Partage public · **Sprint :** Sprint R2

**User Story :**
> En tant que **mainteneur**, je veux **une CI minimale qui lance les validations essentielles**, afin de **sécuriser les contributions et éviter les régressions visibles**.

#### Tâches techniques
- Ajouter un workflow GitHub Actions pour tests Python et `scripts/validate.sh`.
- Vérifier XML/modinfo et fichiers requis.
- Mettre en cache les dépendances Python sans versionner le venv.
- Publier un statut clair pour les pull requests.

#### Critères d'acceptation
✅ Chaque PR exécute les tests et validations de base
✅ Un échec indique clairement le fichier ou la commande en cause

#### Dépendances
- US-035, US-041

---

## EPIC 1 : Qualité des conseils & aide en jeu

**Objectif :** Donner au coach assez de données et de vigilance pour produire des conseils utiles, y compris entre deux analyses longues.
**Statut global :** 📝 0/4 terminées

---

### US-025 : Conseils utiles dès le tour 1

**Statut :** 📝 À faire · **Priorité :** 🔴 Must · **Jalon :** MVP jouable robuste · **Sprint :** Sprint R1

**User Story :**
> En tant que **joueur**, je veux **recevoir un plan d'ouverture concret dès le tour 1**, afin de **tester immédiatement la valeur du coach après avoir choisi mon objectif de victoire**.

#### Contexte debug
- Au tour 1, le gamestate peut être minimal et `_detect_insufficient_context()` répond "contexte insuffisant".
- Ce comportement bloque la recette rapide, alors que le tour 1 peut produire un conseil déterministe utile.

#### Tâches techniques
- Ajouter dans `coach/src/coach.py` une stratégie d'ouverture déterministe basée sur objectif de victoire, civilisation, difficulté, vitesse et taille de carte.
- Assouplir la détection "contexte insuffisant" pour le tour 1.
- Préparer le prompt/fallback pour exploiter les paramètres disponibles même sans villes détaillées.
- Ajouter des tests par objectif de victoire.

#### Critères d'acceptation
✅ Après le choix de victoire au tour 1, le coach propose constructions/unités/technologies initiales
✅ Le message "contexte insuffisant" n'apparaît plus comme réponse nominale au tour 1

#### Dépendances
- US-006, US-019 du backlog v0.1

#### Complément
- US-031 améliorera la qualité de ces conseils quand le gamestate sera enrichi, mais ne doit pas bloquer le conseil d'ouverture déterministe.

---

### US-031 : Gamestate enrichi pour améliorer la qualité des conseils

**Statut :** 📝 À faire · **Priorité :** 🟠 Should · **Jalon :** MVP jouable robuste · **Sprint :** Sprint R1

**User Story :**
> En tant que **coach**, je veux **recevoir davantage d'éléments de partie structurés**, afin de **produire des conseils plus précis sans halluciner sur l'état réel de Civ5**.

#### Tâches techniques
- Enrichir `mod/Lua/GameplayScript.lua` avec nombre de joueurs, cités-états, ères, technologies acquises/en recherche, traits/bonus civilisation, carte utile, voisins, ressources visibles, bâtiments, production en file, promotions.
- Bumper `schema_version` et mettre à jour `coach/src/gamestate_schema.py` + `coach/config/gamestate.schema.v0.json`.
- Adapter prompt LLM et fallback local pour exploiter les nouveaux champs.
- Vérifier la taille du payload stocké via SQLite `SetValue`.

#### Critères d'acceptation
✅ Le coach dispose des données minimales pour conseiller ouverture, recherche, production et voisinage
✅ Le payload reste stable et lisible depuis `ModUserData`
✅ Les anciennes versions de schéma échouent avec un message clair

#### Dépendances
- US-001 du backlog v0.1, US-025

---

### US-032 : Surveillance optionnelle des erreurs et risques de jeu

**Statut :** 📝 À faire · **Priorité :** 🟠 Should · **Jalon :** MVP jouable robuste · **Sprint :** Sprint R1

**User Story :**
> En tant que **joueur**, je veux **activer une surveillance légère à chaque tour pour être prévenu d'une erreur de jeu ou d'un risque important**, afin de **corriger rapidement une menace critique sans attendre la prochaine analyse stratégique complète**.

#### Contexte
- Le coach projette actuellement sur un horizon de 10 tours.
- Certaines situations critiques méritent une alerte immédiate : ville en danger, guerre imminente, bonheur négatif, économie au bord de la faillite, recherche/production incohérente avec l'objectif.

#### Tâches techniques
- Ajouter une option configurable `risk_watch_enabled` et une fréquence indépendante des analyses LLM complètes.
- Implémenter d'abord une surveillance déterministe locale, sans appel LLM systématique.
- Définir des règles d'alerte explicites : bonheur, trésor/or par tour, unités ennemies proches, villes non défendues, production/recherche bloquante.
- Afficher une alerte courte dans l'overlay sans écraser le dernier conseil stratégique.
- Ajouter tests unitaires sur les règles de risque.

#### Critères d'acceptation
✅ La surveillance peut être activée/désactivée sans modifier le code
✅ Une alerte critique peut apparaître entre deux analyses LLM
✅ Le coût LLM n'augmente pas par défaut

#### Dépendances
- US-031, US-033

---

### US-040 : Détection robuste de nouvelle partie et session

**Statut :** 📝 À faire · **Priorité :** 🟠 Should · **Jalon :** MVP jouable robuste · **Sprint :** Sprint R1

**User Story :**
> En tant que **joueur**, je veux **que le coach détecte proprement le début d'une nouvelle partie**, afin de **ne pas mélanger historique, coûts, préférences contextuelles et cache entre deux sessions**.

#### Tâches techniques
- Définir un identifiant de session/partie à partir du gamestate disponible.
- Réinitialiser ou archiver historique, budget, cache et alertes au changement de partie.
- Gérer les retours au tour 1 sans écraser les données utiles de la partie précédente.
- Ajouter tests avec deux fixtures de parties distinctes.

#### Critères d'acceptation
✅ Une nouvelle partie démarre avec historique/cache/budget séparés
✅ Les archives précédentes restent consultables

#### Dépendances
- US-031, US-036

---

## EPIC 3 : Budget & consommation API

**Objectif :** Donner une visibilité simple et fiable sur la consommation réelle des providers LLM utilisés pendant la partie.
**Statut global :** 📝 0/2 terminées

---

### US-036 : Estimation des coûts API Mistral et OpenAI dans l'overlay

**Statut :** 📝 À faire · **Priorité :** 🟠 Should · **Jalon :** Maîtrise budget · **Sprint :** Sprint R1

**User Story :**
> En tant que **joueur**, je veux **voir dans l'overlay une estimation du coût cumulé des appels Mistral et OpenAI, mise à jour tous les 10 tours**, afin de **suivre ma consommation sans quitter la partie**.

#### Contexte
- Le backlog v0.1 couvre déjà une première estimation de coût côté OpenAI.
- La v0.2 introduit Mistral comme provider par défaut : l'estimation doit donc devenir multi-provider.

#### Tâches techniques
- Centraliser les tarifs par provider/modèle dans la configuration ou un module dédié.
- Cumuler les tokens et coûts par provider : Mistral, OpenAI, fallback local à coût nul.
- Mettre à jour l'affichage overlay tous les 10 tours, indépendamment de la fréquence de conseil si nécessaire.
- Afficher un total partie + un détail par provider, avec mention "estimation".
- Prévoir un comportement robuste si le provider ne retourne pas d'usage tokenisé.
- Ajouter tests unitaires sur le calcul de coût multi-provider et le rythme de mise à jour.

#### Critères d'acceptation
✅ L'overlay affiche une estimation de coût cumulée au moins tous les 10 tours
✅ Les coûts Mistral et OpenAI sont distingués
✅ Un appel sans usage tokenisé ne casse pas l'affichage
✅ Le fallback local est compté à coût nul

#### Dépendances
- US-020 du backlog v0.1, US-030, US-034

---

### US-039 : Comparateur Mistral vs OpenAI sur gamestates fixes

**Statut :** 📝 À faire · **Priorité :** 🟢 Could · **Jalon :** Maîtrise budget / qualité · **Sprint :** Sprint R2

**User Story :**
> En tant que **développeur**, je veux **comparer Mistral et OpenAI sur les mêmes gamestates de référence**, afin de **choisir le meilleur compromis qualité, latence, coût et robustesse de parsing**.

#### Tâches techniques
- Constituer un jeu de gamestates fixes : ouverture, milieu de partie, guerre, économie faible, contexte insuffisant.
- Exécuter les deux providers sur les mêmes entrées avec prompts identiques ou équivalents.
- Capturer coût estimé, latence, validité JSON, confiance et qualité subjective.
- Produire un rapport local versionnable sans inclure de secrets ni réponses coûteuses par défaut.

#### Critères d'acceptation
✅ Une commande permet de comparer Mistral et OpenAI sur les mêmes cas
✅ Le rapport aide à choisir le provider/modèle par défaut

#### Dépendances
- US-030, US-036, US-038

---

## Roadmap & Sprints (mise à jour)

### Sprint R0 : Debug & recette jouable
| US |
| --- |
| US-030, US-023, US-024, US-026, US-027, US-028, US-029, US-037 |

**Critère de sortie :** Mistral est opérationnel par défaut ; le coach se lance depuis le dépôt, analyse chaque tour en mode debug et affiche l'overlay correctement.

### Sprint R1 : Maintenabilité puis qualité des conseils
| US |
| --- |
| US-033, US-034, US-035, US-038, US-025, US-031, US-032, US-040, US-036 |

**Critère de sortie :** architecture plus modulaire, diagnostics exploitables et tests de non-régression, puis conseils tour 1, gamestate enrichi, alertes de risque optionnelles et coûts API visibles dans l'overlay.

### Sprint R2 : Durcissement maintenance
| US |
| --- |
| US-041, US-042, US-039 |

**Critère de sortie :** environnement Python clarifié, CI minimale active et comparaison provider exploitable.

---

## Stack technique (macOS)

| Composant | Choix | Justification |
| --- | --- | --- |
| **App Coach** | Python 3.11+ | Cohérent avec la v0.1, simple à recetter localement |
| **UI Overlay** | PyQt6 | Base existante à stabiliser |
| **LLM Provider par défaut cible** | Mistral | Priorité utilisateur pour la v0.2 |
| **LLM Provider alternatif** | OpenAI GPT-4o-mini | Provider existant à conserver et stabiliser |
| **Source gamestate** | SQLite `ModUserData` contenant un payload JSON | Compatible avec les contraintes Civ5 Steam/macOS |
| **Config Storage** | JSON multi-niveaux + Keychain + env vars | Keychain pour les clés API ; JSON pour les préférences non sensibles |

---

## Risques & Mitigations

| Risque | Probabilité | Impact | Mitigation |
| --- | --- | --- | --- |
| Overlay invisible après fermeture | Élevé | Haut | US-023 en Must |
| Erreurs LLM mal classées | Élevé | Moyen | US-024 + tests de retry |
| Mistral pas encore intégré | Élevé | Haut | US-030 en Must |
| Recette lente sans analyse tour par tour | Élevé | Moyen | US-026 + US-027 |
| Données Civ5 insuffisantes pour conseil utile | Moyen | Haut | US-025 pour le tour 1, US-031 pour enrichir le gamestate |
| Installation macOS incohérente avec SQLite | Moyen | Haut | US-028 + US-029 |
| Dette technique freinant les providers et le gamestate | Moyen | Haut | US-033 à US-035 |
| Surveillance de risque trop bruyante | Moyen | Moyen | US-032 optionnelle, règles déterministes testées, pas d'alerte LLM par défaut |
| Estimation de coût imprécise selon provider | Moyen | Moyen | US-036 : affichage "estimation", tarifs configurables, fallback si usage absent |
| `.venv` versionné ou modifié localement | Élevé | Moyen | US-037 pour audit/conservation, US-041 pour nettoyage futur |

---

## Notes de mise à jour

**10 juillet 2026 (ajustement des priorités v0.2)**
- US-030 placée comme priorité n°1 de l'EPIC 0
- US-025 déplacée dans l'EPIC 1
- EPIC 2 placé avant EPIC 1 dans la synthèse, l'ordre du document et la roadmap R1

**10 juillet 2026 (ajout budget API v0.2)**
- Ajout de l'EPIC 3 Budget & consommation API
- Ajout de l'US-036 : estimation des coûts Mistral et OpenAI dans l'overlay, mise à jour tous les 10 tours

**10 juillet 2026 (ajout propositions complémentaires)**
- Ajout des US-037 à US-042 : audit `.venv`, replay fixtures SQLite, comparateur providers, détection nouvelle partie, nettoyage versionnement Python, CI minimale

**10 juillet 2026 (création v0.2 depuis TODO)**
- Création d'un backlog v0.2 séparé du backlog initial v0.1
- Intégration des tâches TODO : overlay, erreurs OpenAI, tour 1, gamestate enrichi, mode debug, scripts de run, installation, documentation, Mistral, surveillance des erreurs/risques de jeu
- Ajout des tâches complémentaires de qualité de code : découplage, observabilité, tests de non-régression

---

**Prochaine revue de backlog :** après Sprint R0 (validation debug/recette jouable avec Mistral)
