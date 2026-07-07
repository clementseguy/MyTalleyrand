# BACKLOG MyTalleyrand

**Date de mise à jour :** 7 juillet 2026
**Version :** 2.0
**Sprint actuel :** Sprint 0 - MVP Technique

> **Contexte du projet :** projet perso d'exploration des outils de développement assisté par IA (agentic AI). Le backlog ci-dessous est structuré pour être exécuté par un agent de développement IA (Codex ou équivalent) jusqu'à complétion.

---

## Définitions de succès (jalons)

Deux jalons distincts pilotent les priorités de ce backlog — ne pas les confondre :

| Jalon | Définition | Portée |
| --- | --- | --- |
| **MVP jouable** | J'ai joué une **partie complète** de Civilization V avec des **conseils utiles** du coach, sans blocage technique, **sous 2€ de coût LLM** (mode difficile). | US du jalon "MVP" ci-dessous |
| **Partage public** | Le repo GitHub est **public**, cloné et utilisé par un tiers technique sans mon assistance directe. | Ajoute doc + tests + onboarding au jalon MVP |

**Contraintes actées :**
- Plateforme : **macOS uniquement** pour ce cycle (portage Windows non engagé, incertain).
- Distribution : **repo GitHub public en l'état** (pas de packaging `.app` grand public, pas d'installeur).
- UI : **aucun asset visuel issu de Civ5/Firaxis** (portrait, sprites, fonts propriétaires) — zéro risque de droits d'auteur.
- Budget LLM : **< 2€ par partie en mode difficile**, avec fréquence d'analyse **configurable** comme levier d'ajustement.
- Qualité : niveau élevé visé, pas de "vibe coding" — le projet sert aussi à évaluer ce qu'on peut attendre des outils de dev IA.

---

## Vue d'ensemble

| Métrique | Valeur |
| --- | --- |
| **Total User Stories** | 22 |
| **US Terminées** | 7 |
| **US En cours (partielles)** | 5 |
| **US À faire** | 9 |
| **US Won't** | 1 |
| **Progression** | 7/21 actives — 33% |

### Répartition par Epic

| Epic | US | Jalon dominant | Statut |
| --- | --- | --- | --- |
| EPIC 1 : Fondations techniques | 5 | MVP | ✅ 3/5 terminées, 🔄 2/5 partielles |
| EPIC 2 : Interface utilisateur | 3 | MVP | 🔄 2/3 partielles, 📝 1/3 à faire |
| EPIC 3 : Logique du coach | 5 | MVP | ✅ 2/5 terminées, 🔄 1/5 partielle, 📝 2/5 à faire |
| EPIC 4 : Maîtrise du budget & optimisation | 6 | MVP (budget) / Could | 📝 5/6 à faire, ⚪ 1 Won't |
| EPIC 5 : Documentation, tests & partage | 4 | Partage public | ✅ 2/4 terminées, 📝 2/4 à faire |

### Légende des statuts

- 📝 **À faire** · 🔄 **En cours** · ✅ **Terminé** · ⏸️ **En attente** · 🚫 **Abandonné**

### Légende MoSCoW

- 🔴 **Must** (bloquant pour un jalon) · 🟠 **Should** (fort impact, non bloquant) · 🟢 **Could** (confort) · ⚪ **Won't** (hors périmètre pour ce cycle)

---

## EPIC 1 : Fondations techniques

**Objectif :** Mettre en place l'infrastructure de base et sa robustesse minimale (Civ5 ↔ app ↔ LLM).
**Statut global :** ✅ 3/5 terminées, 🔄 2/5 partielles

---

### US-001 : Collecte de données de jeu

**Statut :** ✅ Terminé · **Priorité :** 🔴 Must · **Jalon :** MVP · **Sprint :** Sprint 0

**Implémentation :** `mod/Lua/GameplayScript.lua` — export atomique JSON (tmp + rename), `pcall` crash-safety, schéma v0.1.0

**User Story :**
> En tant que **mod Lua**, je veux **exporter l'état du jeu dans un format JSON structuré à chaque tour**, afin que **l'application externe puisse l'analyser**.

#### Tâches techniques
- Rechercher l'API Lua disponible dans Civ5 (`Game.*`, `Players.*`, `Map.*`) et ses limitations
- Créer `CollectGameState()` : paramètres de partie, ressources, villes, unités, technologies, diplomatie
- Exporter en JSON dans `~/Documents/Aspyr/Sid Meier's Civilization 5/MODS/MyTalleyrand/export/` (gérer permissions macOS/Gatekeeper/SIP)
- Encoder en JSON (pas de lib native Lua) et gérer les erreurs d'écriture (`pcall`, logs `Lua.log`)

#### Critères d'acceptation
✅ Fichier JSON généré à chaque tour, format validé
✅ Performance < 100ms par export
✅ Fonctionne sur macOS 13+ (Ventura, Sonoma)
✅ Pas de crash du jeu lors de l'export

#### Dépendances
- Aucune

#### Risques
- Limitations API Lua non documentées · Permissions fichiers macOS

---

### US-002 : Application coach externe — Squelette

**Statut :** ✅ Terminé · **Priorité :** 🔴 Must · **Jalon :** MVP · **Sprint :** Sprint 0

**Implémentation :** `coach/src/` — structure modulaire Python (`main.py`, `watcher.py`, `coach.py`, `llm_client.py`, `overlay.py`, `config.py`, `gamestate_schema.py`, `keychain.py`). Polling `stat.st_mtime_ns` (0.5s), déduplication par `turn_id`, logging fichier + stdout.

> Note : le file watching utilise du polling simple (pas `watchdog`). Migration possible en amélioration future.

**User Story :**
> En tant qu'**utilisateur**, je veux **une application qui tourne en arrière-plan et détecte les nouveaux états de jeu**, afin de **recevoir des conseils sans action manuelle**.

#### Tâches techniques
- Stack : Python 3.11+ (natif macOS, simple pour MVP)
- Structure modulaire (`file_watcher.py`, `llm_client.py`, `game_analyzer.py`, `ui/overlay.py`)
- Lecture de `gamestate.json` + polling via `watchdog`
- Logging dans `~/coach.log`
- Script de lancement macOS double-cliquable (`start_coach.command`)

#### Critères d'acceptation
✅ Démarre sans erreur sur macOS 13+ · ✅ Détecte un nouveau tour en < 2s
✅ CPU < 5% en idle, RAM < 200MB · ✅ Logs clairs et exploitables

#### Dépendances
- US-001

#### Risques
- Overlay complexe sur macOS Sonoma · Performance file watching

---

### US-003 : Intégration API LLM

**Statut :** ✅ Terminé · **Priorité :** 🔴 Must · **Jalon :** MVP · **Sprint :** Sprint 0

**Implémentation :** `coach/src/llm_client.py` — OpenAI GPT-4o-mini, retry exponentiel (`tenacity`), parsing strict `LLMAdvice`, fallback local déterministe. Config multi-niveaux (`settings.json` → Keychain macOS via `keyring` → `coach.user.json` legacy → env vars). `coach/src/keychain.py` stocke, récupère et supprime les clés API via le service Keychain `MyTalleyrand`.

**User Story :**
> En tant que **coach**, je veux **envoyer l'état du jeu à un LLM et parser une réponse structurée**, afin de **produire des recommandations stratégiques**.

#### Tâches techniques
- Provider par défaut : GPT-4o-mini (coût/qualité), architecture ouverte à Anthropic/Ollama (cf. US-011)
- Prompt système "coach stratégique" (analyse, objectif 10 tours, actions concrètes)
- Parsing structuré de la réponse (`analysis`, `objective`, `actions`)
- Retry + backoff sur erreurs réseau (`tenacity`), rate limiting
- Stockage sécurisé de la clé API via **macOS Keychain** (`keyring`)

#### Critères d'acceptation
✅ Appel API réussi, réponse parsée en JSON
✅ Temps de réponse < 10s (95e percentile) · ✅ Coût estimé < $0.05 par analyse
✅ Clé API stockée dans le Keychain via `keyring`; le fichier JSON utilisateur ne contient plus de clé en nouvelle installation

#### Dépendances
- US-002

#### Risques
- Coût cumulé sur partie longue (200+ tours) · Latence réseau variable

---

### US-015 : Gestion d'erreur — gamestate manquant/corrompu *(proposition ajoutée)*

**Statut :** 🔄 En cours · **Priorité :** 🔴 Must · **Jalon :** MVP · **Sprint :** Sprint 0

**Implémentation partielle :** `gamestate_schema.py` valide le schéma (champs requis, types, version). `watcher.py` gère JSON corrompu et schéma invalide sans crash (logs warning). `overlay.py` et `coach.py` résistent aux fichiers d'état corrompus (try/except).

**Reste à faire :** notification utilisateur dans l'overlay (actuellement logs uniquement).

**User Story :**
> En tant qu'**utilisateur**, je veux **être averti clairement si `gamestate.json` est absent, vide ou corrompu**, afin de **comprendre la panne sans croire l'app buguée**.

#### Tâches techniques
- Détecter fichier absent / JSON invalide / champs requis manquants
- Message utilisateur explicite dans l'overlay (pas seulement dans les logs)
- Suggestion d'action (vérifier permissions dossier MODS, consulter `Lua.log`)

#### Critères d'acceptation
✅ Aucun crash silencieux de l'app coach sur gamestate invalide
✅ Message affiché à l'utilisateur en < 5s après détection

#### Dépendances
- US-001, US-002

---

### US-016 : Gestion d'erreur réseau/LLM *(proposition ajoutée)*

**Statut :** 🔄 En cours · **Priorité :** 🔴 Must · **Jalon :** MVP · **Sprint :** Sprint 0

**Implémentation partielle :** retry exponentiel (`tenacity`, 3 tentatives) + fallback local déterministe si LLM indisponible. La partie n'est jamais bloquée.

**Reste à faire :** statut UX visible dans l'overlay ("Reconnexion en cours…", "Fallback activé").

**User Story :**
> En tant qu'**utilisateur**, je veux **un message clair et une reprise automatique en cas de timeout ou perte réseau LLM**, afin de **ne pas rester bloqué sans feedback pendant ma partie**.

#### Tâches techniques
- Réutilise le retry de US-003, ajoute une couche UX : statut visible ("Reconnexion en cours...")
- Si échec après N tentatives : message clair + reprise automatique au tour suivant (pas de blocage de partie)

#### Critères d'acceptation
✅ Une panne réseau ponctuelle n'interrompt jamais la partie
✅ L'utilisateur voit toujours pourquoi il n'a pas reçu de conseil

#### Dépendances
- US-003

---

## EPIC 2 : Interface utilisateur

**Objectif :** Overlay fonctionnel, non intrusif, sans dépendance à des assets propriétaires.
**Statut global :** 🔄 2/3 partielles, 📝 1/3 à faire

---

### US-004 : Overlay de base

**Statut :** 🔄 En cours · **Priorité :** 🔴 Must · **Jalon :** MVP · **Sprint :** Sprint 1

**Implémentation partielle :** `coach/src/overlay.py` — abstraction testable avec position persistante, toggle visibilité, rendu texte des conseils (`show_advice`). Pas de dépendance PyQt6 au runtime.

**Reste à faire :** fenêtre PyQt6 réelle, click passthrough, détection fenêtre Civ5, support multi-écrans.

**User Story :**
> En tant qu'**utilisateur**, je veux **voir les conseils du coach superposés sur le jeu**, afin de **ne pas avoir à alt-tab**.

#### Tâches techniques
- PyQt6, fenêtre transparente `WindowStaysOnTopHint` + `FramelessWindowHint`
- Détection de la fenêtre Civ5 (mode fenêtré requis) et positionnement multi-écrans
- Passthrough des clics hors zone de conseils, update rate max 30 FPS
- Vérification permission macOS "Accessibilité" (`AXIsProcessTrusted`)

#### Critères d'acceptation
✅ Overlay visible par-dessus Civ5 en mode fenêtré, ne bloque pas les clics sur le jeu
✅ Position persistante entre sessions · ✅ Fonctionne multi-écrans · ✅ Pas de lag perceptible du jeu

#### Dépendances
- US-002, US-003

#### Risques
- Mode plein écran incompatible avec l'overlay (limitation connue, à documenter)

---

### US-017 : Fermer / réduire l'overlay *(proposition ajoutée)*

**Statut :** 🔄 En cours · **Priorité :** 🔴 Must · **Jalon :** MVP · **Sprint :** Sprint 1

**Implémentation partielle :** `toggle_visibility()` et persistance de l'état visible/masqué dans `overlay_state.json`.

**Reste à faire :** boutons fermer/réduire dans l'UI réelle (dépend de US-004 PyQt6).

**User Story :**
> En tant qu'**utilisateur**, je veux **pouvoir fermer ou réduire l'overlay à tout moment**, afin de **ne pas être gêné visuellement quand je n'ai pas besoin de conseil**.

#### Tâches techniques
- Boutons fermer/réduire sur l'overlay
- État "réduit" persistant jusqu'au prochain conseil déclenché

#### Critères d'acceptation
✅ L'overlay peut être masqué sans quitter l'application
✅ L'état réduit/fermé ne bloque pas la détection des tours suivants

#### Dépendances
- US-004

---

### US-005 : Interface soignée sans assets propriétaires

**Statut :** 📝 À faire · **Priorité :** 🟠 Should · **Jalon :** MVP (confort) · **Sprint :** Sprint 3

**User Story :**
> En tant qu'**utilisateur**, je veux **une interface claire et lisible (texte + icônes génériques, typographie libre)**, afin d'**avoir une expérience agréable sans aucun risque de droits d'auteur**.

> **Décision actée :** pas de portrait de Talleyrand ni d'assets/fonts issus de Civ5/Firaxis, même stylisés. Design 100% original (icônes libres type Material/Font Awesome, police libre type Google Fonts).

#### Tâches techniques
- Mockup simple (sections : objectif courant, actions catégorisées, historique court)
- Style QSS avec palette et police originales, adapté HiDPI/Retina
- Animation légère d'apparition (fade-in)

#### Critères d'acceptation
✅ Aucune ressource graphique ou typographique issue de Civ5/Firaxis
✅ Lisible sur écran Retina · ✅ Cohérent visuellement d'un bout à l'autre de l'app

#### Dépendances
- US-004

---

## EPIC 3 : Logique du coach

**Objectif :** Rendre les conseils réellement utiles sur toute la durée d'une partie.
**Statut global :** ✅ 2/5 terminées, 🔄 1/5 partielle, 📝 2/5 à faire

---

### US-006 : Dialogue d'initialisation (Tour 1)

**Statut :** 🔄 En cours · **Priorité :** 🟠 Should · **Jalon :** MVP · **Sprint :** Sprint 1

**Implémentation partielle :** `--victory-focus` CLI (domination/science/culture/diplomatie/équilibrée), `set_victory_focus()` dans `CoachingEngine`, transmis au prompt LLM.

**Reste à faire :** popup UI au tour 1, détection auto paramètres de partie (difficulté, carte, vitesse).

**User Story :**
> En tant que **joueur**, je veux **indiquer ma stratégie de victoire au tour 1**, afin que **le coach adapte ses conseils**.

#### Tâches techniques
- Popup au tour 1 (types de victoire : Domination, Science, Culture, Diplomatie, Score)
- Détection auto des paramètres de partie (difficulté, taille carte, vitesse)
- Sauvegarde des préférences (`user_preferences.json`), transmises au prompt LLM

#### Critères d'acceptation
✅ Popup affiché au tour 1 uniquement · ✅ Préférences réutilisées à chaque analyse

#### Dépendances
- US-004

---

### US-007 : Analyse cyclique (objectif court terme)

**Statut :** ✅ Terminé · **Priorité :** 🔴 Must · **Jalon :** MVP · **Sprint :** Sprint 2

**Implémentation :** `coach/src/coach.py` — `get_decision()` déclenche l'analyse au tour 1 + tous les 10 tours (`turn_number % 10`). Objectif 10 tours dans `LLMAdvice.objective_10_turns`.

**User Story :**
> En tant que **coach**, je veux **analyser la partie à intervalle régulier**, afin de **proposer un objectif actionnable à court terme**.

> Note : l'intervalle par défaut est 10 tours, mais devient configurable via US-011 (levier budget).

#### Tâches techniques
- Déclencheur configurable (`turn == 1 or turn % N == 0`)
- Prompt "analyse de situation" → un objectif SMART aligné sur la stratégie de victoire
- Affichage prominent dans l'overlay + historique des objectifs

#### Critères d'acceptation
✅ Analyse déclenchée à l'intervalle configuré, exactement
✅ Objectif clair, actionnable, historique consultable

#### Dépendances
- US-003, US-004

---

### US-008 : Recommandations d'actions

**Statut :** ✅ Terminé · **Priorité :** 🔴 Must · **Jalon :** MVP · **Sprint :** Sprint 2

**Implémentation :** `LLMAdvice` dataclass — 3-5 `priority_actions`, `categories` (economie/science/militaire/diplomatie), `risks`, `confidence` (0-100). Parsing strict + normalisation.

**User Story :**
> En tant que **joueur**, je veux **recevoir des actions concrètes et catégorisées**, afin de **progresser vers mon objectif**.

#### Tâches techniques
- Prompt structuré → 3-5 actions catégorisées (construction/science/diplomatie/militaire/économie/culture)
- Affichage checklist interactive, tooltips explicatifs (pourquoi cette action)
- Suivi de progression (% actions réalisées)

#### Critères d'acceptation
✅ 3-5 actions par analyse, claires et réalisables in-game
✅ Catégorisées, priorisées, avec justification courte

#### Dépendances
- US-007

---

### US-018 : Changement de stratégie en cours de partie *(proposition ajoutée)*

**Statut :** 📝 À faire · **Priorité :** 🟠 Should · **Jalon :** MVP (confort) · **Sprint :** Sprint 2

**User Story :**
> En tant que **joueur**, je veux **pouvoir changer ma stratégie de victoire en cours de partie**, afin de **m'adapter si la situation géopolitique évolue**.

#### Tâches techniques
- Accès à un panneau de préférences depuis l'overlay (pas seulement au tour 1)
- Mise à jour immédiate du contexte envoyé au LLM à la prochaine analyse

#### Critères d'acceptation
✅ Le changement de stratégie est pris en compte dès l'analyse suivante

#### Dépendances
- US-006, US-007

---

### US-019 : Signalement d'un contexte insuffisant *(proposition ajoutée)*

**Statut :** 📝 À faire · **Priorité :** 🟠 Should · **Jalon :** MVP (confort) · **Sprint :** Sprint 2

**User Story :**
> En tant que **joueur**, je veux **que le coach signale explicitement s'il manque de contexte** (ex : tour 1, pas encore de ville), afin de **ne pas recevoir de conseils incohérents ou hallucinés**.

#### Tâches techniques
- Heuristique simple côté prompt/parsing (détection de champs vides/peu significatifs)
- Message distinct de l'erreur réseau ("contexte insuffisant" ≠ "panne")

#### Critères d'acceptation
✅ Aucun conseil affiché comme "certain" quand le contexte est notoirement pauvre

#### Dépendances
- US-003, US-007

---

## EPIC 4 : Maîtrise du budget & optimisation

**Objectif :** Garantir le respect du budget cible (< 2€/partie difficile) et offrir des réglages avancés.
**Statut global :** 📝 5/6 à faire, ⚪ 1 Won't

---

### US-009 : Cache et évitement des appels redondants

**Statut :** 📝 À faire · **Priorité :** 🔴 Must · **Jalon :** MVP (budget) · **Sprint :** Sprint 2/3

**User Story :**
> En tant qu'**utilisateur**, je veux **que l'application mette en cache les réponses LLM et évite de ré-analyser un contexte inchangé**, afin de **réduire les coûts et la latence sur une partie longue**.

#### Tâches techniques
- Clé de cache basée sur un hash du contexte pertinent (tour, ressources, objectif)
- Court-circuit de l'appel LLM si rien de significatif n'a changé depuis la dernière analyse

#### Critères d'acceptation
✅ Pas de double appel LLM pour un contexte quasi identique
✅ Contribue mesurablement à tenir le budget < 2€/partie difficile

#### Dépendances
- US-003, US-007

---

### US-011 : Fréquence d'analyse et niveau de détail configurables

**Statut :** 📝 À faire · **Priorité :** 🔴 Must · **Jalon :** MVP (budget) · **Sprint :** Sprint 3

**User Story :**
> En tant qu'**utilisateur**, je veux **configurer la fréquence d'analyse du coach (ex : tous les 5/10/20 tours) et le niveau de détail des réponses**, afin de **maîtriser mon budget LLM selon le mode de jeu**.

#### Tâches techniques
- Fichier de config utilisateur (`settings.json`) exposant `analysis_interval`, `detail_level`
- Documentation de l'impact coût/fréquence (ordre de grandeur, pas de garantie chiffrée)

#### Critères d'acceptation
✅ La fréquence par défaut (10 tours) est modifiable sans redémarrage de partie
✅ Un réglage plus économe permet de rester sous 2€ sur une partie difficile longue

#### Dépendances
- US-003, US-007, US-009

---

### US-020 : Estimation et alerte de coût cumulé *(proposition ajoutée)*

**Statut :** 📝 À faire · **Priorité :** 🟠 Should · **Jalon :** MVP (confort budget) · **Sprint :** Sprint 3

**User Story :**
> En tant qu'**utilisateur**, je veux **voir une estimation du coût LLM cumulé en cours de partie et être alerté en cas de dépassement de mon plafond**, afin de **garder la main sur ma dépense sans avoir à la calculer moi-même**.

#### Tâches techniques
- Calcul du coût par appel (tokens × tarif provider), cumul affiché dans l'overlay
- Seuil configurable avec alerte visuelle simple

#### Critères d'acceptation
✅ Le coût cumulé affiché est cohérent (± marge raisonnable) avec la facturation réelle du provider

#### Dépendances
- US-003, US-011

---

### US-010 : Historique des conseils

**Statut :** 📝 À faire · **Priorité :** 🟢 Could · **Jalon :** amélioration post-MVP · **Sprint :** Sprint 4+

**User Story :**
> En tant que **joueur**, je veux **consulter l'historique des conseils passés (filtrable, exportable)**, afin de **revoir ma stratégie**.

#### Critères d'acceptation
✅ Historique consultable dans l'overlay, filtrable par tour/catégorie

#### Dépendances
- US-007, US-008

---

### US-011b : Choix du provider/modèle LLM

**Statut :** 📝 À faire · **Priorité :** 🟢 Could · **Jalon :** amélioration post-MVP · **Sprint :** Sprint 4+

**User Story :**
> En tant qu'**utilisateur avancé**, je veux **choisir mon provider/modèle LLM (OpenAI, Anthropic, local)**, afin d'**arbitrer coût, qualité et vie privée**.

#### Critères d'acceptation
✅ Changement de provider possible via config, sans modification de code

#### Dépendances
- US-003

---

### US-012 : Mode hors-ligne (LLM local)

**Statut :** 📝 À faire · **Priorité :** ⚪ Won't (ce cycle) · **Jalon :** hors périmètre

**User Story :**
> En tant qu'**utilisateur sans connexion**, je veux **utiliser un LLM local (Ollama)**, afin de **jouer hors-ligne**.

**Justification Won't :** hors du périmètre actuel (exploration agentic AI + macOS uniquement, pas de besoin offline exprimé). À reconsidérer si le projet évolue.

---

## EPIC 5 : Documentation, tests & partage public

**Objectif :** Rendre le repo utilisable par un tiers technique, sans mon assistance.
**Statut global :** ✅ 2/4 terminées, 📝 2/4 à faire
**Jalon :** Partage public (non requis pour le jalon MVP jouable)

---

### US-013 : Documentation utilisateur

**Statut :** ✅ Terminé · **Priorité :** 🟠 Should · **Jalon :** Partage public · **Sprint :** Sprint 3

**Implémentation :** `README.md` (racine + coach + mod), `docs/README.md` (architecture), `docs/MACOS_GUIDE.md` (chemins, permissions, packaging), `docs/TESTING.md`, `docs/BACKLOG.md`. Script `install_macos.sh` avec onboarding interactif (clé API, prompt).

**User Story :**
> En tant qu'**utilisateur technique consultant le repo public**, je veux **une documentation d'installation claire (README, config API, troubleshooting)**, afin de **pouvoir cloner et faire fonctionner l'app moi-même**.

#### Tâches techniques
- README : prérequis macOS, installation mod + app, configuration clé API
- Section troubleshooting (permissions, gamestate manquant, overlay invisible en plein écran)

#### Critères d'acceptation
✅ Un tiers technique peut installer l'app en suivant uniquement le README

#### Dépendances
- US-001 à US-011 (fonctionnalités à documenter)

---

### US-014 : Tests et validation

**Statut :** ✅ Terminé · **Priorité :** 🟠 Should · **Jalon :** Partage public · **Sprint :** Sprint 3

**Implémentation :** 19 tests pytest (7 fichiers + conftest.py) — config, LLM client, watcher, coach engine, overlay, gamestate schema, intégration pipeline. `validate.sh` (fichiers requis + XML + pytest). Smoke test `first_test.sh`.

**User Story :**
> En tant que **développeur**, je veux **des tests unitaires et d'intégration sur le pipeline Lua → JSON → LLM → Overlay**, afin de **fiabiliser l'app avant de la rendre publique**.

#### Tâches techniques
- Tests unitaires Python (file watcher, parsing LLM, cache)
- Test d'intégration bout-en-bout + test en partie réelle (0-200 tours)

#### Critères d'acceptation
✅ Coverage tests > 70% · ✅ Partie de 200 tours sans crash

#### Dépendances
- US-001 à US-011

---

### US-021 : Onboarding premier lancement *(proposition ajoutée)*

**Statut :** 📝 À faire · **Priorité :** 🟢 Could · **Jalon :** Partage public (confort) · **Sprint :** Sprint 4+

**User Story :**
> En tant qu'**utilisateur**, je veux **un mode "premier lancement" qui vérifie les permissions macOS requises et me guide pas à pas**, afin de **réussir l'installation sans lire toute la doc en détail**.

**Justification Could :** public cible = développeurs clonant un repo GitHub, capables de suivre un README (US-013) ; confort, pas indispensable.

#### Dépendances
- US-013

---

### US-022 : Désinstallation propre *(proposition ajoutée)*

**Statut :** 📝 À faire · **Priorité :** 🟢 Could · **Jalon :** Partage public (confort) · **Sprint :** Sprint 4+

**User Story :**
> En tant qu'**utilisateur**, je veux **pouvoir désinstaller proprement l'app et révoquer ma clé API du Keychain**, afin de **ne pas laisser de résidus sensibles**.

**Justification Could :** repo public sans installeur = public technique, risque résiduel faible.

#### Dépendances
- US-003

---

## Roadmap & Sprints (mise à jour)

### Sprint 0 : MVP Technique
| US | Points* |
| --- | --- |
| US-001, US-002, US-003, US-015, US-016 | — |

**Critère de sortie :** gamestate JSON → LLM → réponse texte, avec gestion d'erreurs de base.

### Sprint 1 : Interface de base
| US |
| --- |
| US-004, US-017, US-006 |

**Critère de sortie :** overlay fonctionnel, fermable, affichant des conseils.

### Sprint 2 : Logique coach
| US |
| --- |
| US-007, US-008, US-009, US-018, US-019 |

**Critère de sortie :** objectifs + actions recommandées, coût maîtrisé par le cache.

### Sprint 3 : Polish MVP + budget + partage
| US |
| --- |
| US-005, US-011, US-020, US-013, US-014 |

**Critère de sortie (MVP jouable) :** partie complète jouée avec conseils utiles, sous 2€, atteint dès la fin du Sprint 2 en pratique — le Sprint 3 vise le jalon **Partage public**.

### Sprint 4+ : Améliorations optionnelles
| US |
| --- |
| US-010, US-011b, US-021, US-022, (US-012 Won't) |

*Estimation en points volontairement omise sur les US ajoutées — à chiffrer par l'agent de développement lors du planning de sprint.*

---

## Stack technique (macOS)

| Composant | Choix | Justification |
| --- | --- | --- |
| **App Coach** | Python 3.11+ | Natif macOS, simple pour MVP |
| **UI Overlay** | PyQt6 | Fonctionne sur Apple Silicon |
| **LLM Provider (défaut)** | OpenAI GPT-4o-mini | Bon rapport qualité/coût, architecture ouverte (US-011b) |
| **File Watch** | polling `stat.st_mtime_ns` | Implémentation actuelle simple et fonctionnelle ; migration watchdog possible |
| **Config Storage** | JSON multi-niveaux + Keychain + env vars | Keychain (`keyring`) intégré pour la clé API ; JSON réservé aux préférences non sensibles |

---

## Risques & Mitigations

| Risque | Probabilité | Impact | Mitigation |
| --- | --- | --- | --- |
| Overlay complexe sur Sonoma | Moyen | Haut | Fallback menu bar app si besoin |
| Coût LLM trop élevé | Moyen | Moyen | US-009 (cache) + US-011 (fréquence configurable) — traités en Must |
| Permissions macOS | Moyen | Moyen | US-015 + doc troubleshooting (US-013) |
| Risque de droits d'auteur (assets Civ5) | Faible (traité) | Haut si ignoré | US-005 : UI 100% originale, décision actée |

---

## Notes de mise à jour

**7 juillet 2026 (US-003 terminée)**
- Intégration Keychain via `keyring` pour la clé API OpenAI
- Suppression de `llm.api_key` de l’exemple de configuration utilisateur et stockage Keychain par l’installateur macOS
- Statuts ajustés : 7 US terminées, 5 partielles, 9 à faire, 1 Won’t

**7 juillet 2026 (sync statuts)**
- Synchronisation des statuts v2 avec le code existant : 7 US terminées, 5 partielles, 9 à faire
- Ajout des références d'implémentation pour chaque US terminée/partielle
- Stack technique ajustée (polling réel vs watchdog planifié, Keychain stubs)
- Améliorations techniques non planifiées déjà appliquées : centralisation prompts, robustesse JSON corrompu, pcall mod Lua

**7 juillet 2026 (restructuration v2)**
- Ajout de 8 US suite à revue de backlog (US-015 à US-022) : gestion d'erreurs, contrôle overlay, maîtrise budget, partage public
- Deux jalons distincts introduits : MVP jouable / Partage public
- US-005 recadrée : suppression de toute dépendance à des assets Civ5/Firaxis
- US-009 et US-011 remontées en Must (contrainte budget < 2€/partie confirmée, configurable)
- US-013/US-014 repositionnées sur le jalon Partage public plutôt que MVP
- US-012 (LLM local) confirmée Won't pour ce cycle

**22 décembre 2025**
- Création du backlog initial (14 US, 115 points, roadmap 4 sprints)

---

**Prochaine revue de backlog :** après le Sprint 2 (validation du jalon MVP jouable)