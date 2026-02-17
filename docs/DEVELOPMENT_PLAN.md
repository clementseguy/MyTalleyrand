# Plan de développement autonome — MyTalleyrand

Ce plan transforme le backlog en exécution concrète pour livrer un MVP jouable puis une V1 stable.

## 1. Objectif produit

Livrer un système en 3 composants, connecté de bout en bout :

1. **Mod Civ5 (Lua/XML/SQL)** : exporte l’état de partie en JSON à chaque tour.
2. **Coach Python** : détecte les nouveaux tours, analyse l’état, génère des conseils via LLM.
3. **Overlay PyQt6** : affiche les conseils en surcouche pendant la partie (mode fenêtré).

## 2. Cibles de réussite (MVP)

- Détection nouveau tour < 2 secondes.
- Export Lua stable (aucun crash sur session de 30 tours).
- Conseils affichés en < 12 secondes après nouveau tour.
- Overlay lisible, non bloquant, stable pendant 60 minutes.
- Gestion d’échec robuste (fichier corrompu, API indisponible, timeout).

## 3. Architecture technique cible

## 3.1 Pipeline de données

`Civ5 Lua -> gamestate.json -> watcher Python -> analyzer -> llm_client -> formatter -> overlay`

## 3.2 Contrats de données

- **Entrée** : `gamestate.json` versionné (`schema_version`).
- **Sortie LLM normalisée** :
  - `objective_10_turns` (string)
  - `priority_actions` (liste 3-5 items)
  - `risks` (liste)
  - `confidence` (0-100)

## 3.3 Principes de robustesse

- Écriture atomique JSON (`tmp + rename`).
- Déduplication par `turn_id`.
- Retry exponentiel + timeout côté LLM.
- Fallback local si appel LLM impossible.

## 4. Roadmap d’implémentation

## Phase 0 — Setup (2-3 jours)

**Objectif** : base de développement propre et testable.

- Créer structure coach (`src/`, `tests/`, `config/`, `logs/`).
- Ajouter `settings.json` + variables d’environnement.
- Ajouter scripts standards (run, test, lint).
- Définir schéma `gamestate.json` v0.

**Livrable** : app Python démarre localement + tests de base exécutables.

## Phase 1 — Export Civ5 + ingestion (US-001, US-002)

**Objectif** : flux données fiable entre jeu et app.

- Implémenter `CollectGameState()` Lua.
- Export JSON à chaque tour.
- Lire/valider JSON dans le coach.
- Dédupliquer les tours déjà traités.
- Journaliser chaque tour détecté.

**Critères d’acceptation**
- JSON valide généré à chaque tour.
- Détection tour < 2s.
- 0 crash sur test 30 tours.

## Phase 2 — Intégration LLM (US-003)

**Objectif** : produire un conseil structuré et exploitable.

- Implémenter `llm_client.py` (provider principal + fallback).
- Implémenter prompt système + prompt d’analyse.
- Parser la réponse en format strict.
- Gérer erreurs réseau, timeout, quota.

**Critères d’acceptation**
- >95% réponses parseables.
- Temps moyen < 10s.
- Message utilisateur explicite en cas d’échec.

## Phase 3 — Overlay MVP (US-004)

**Objectif** : afficher les conseils in-game.

- Fenêtre transparente top-most.
- Position persistante.
- Affichage : objectif + 3-5 actions.
- Raccourcis simples (masquer/afficher).

**Critères d’acceptation**
- Overlay visible 60 min sans crash.
- CPU idle < 5%.
- Aucun blocage majeur des clics jeu.

## Phase 4 — Logique coach (US-006, US-007, US-008)

**Objectif** : passer d’un affichage brut à un coaching utile.

- Dialogue tour 1 (objectif de victoire).
- Analyse tous les 10 tours.
- Recommandations catégorisées : économie, science, militaire, diplomatie.
- Historique local minimal des conseils.

**Critères d’acceptation**
- Déclenchement exact (tour 1, puis tous les 10 tours).
- Conseils actionnables et cohérents avec la partie.

## Phase 5 — Stabilisation et recette (US-014)

**Objectif** : rendre le MVP publiable pour tests élargis.

- Tests d’intégration bout en bout (données simulées + session réelle).
- Gestion complète des erreurs critiques.
- Checklist de recette + doc opératoire.

**Go/No-Go MVP**
- 10 parties courtes sans crash bloquant.
- Taux d’erreur critique < 2%.
- Latence conseil affiché < 12s (moyenne).

## 5. Plan d’exécution hebdomadaire (proposé)

- **Semaine 1** : Phase 0 + Phase 1
- **Semaine 2** : Phase 2 + début Phase 3
- **Semaine 3** : fin Phase 3 + Phase 4
- **Semaine 4** : Phase 5 + documentation de release

## 6. Backlog opérationnel immédiat (prochain commit de dev)

1. Créer `coach/src/file_watcher.py` (watch + déduplication tour).
2. Créer `coach/src/gamestate_schema.py` (validation minimale du JSON).
3. Créer `coach/src/llm_client.py` (interface + mock).
4. Créer `coach/src/ui/overlay.py` (fenêtre MVP).
5. Ajouter tests unitaires sur parsing gamestate + déclenchement tours.

## 7. Risques clés et mitigation

- **Permissions macOS/overlay** : documenter prérequis et imposer mode fenêtré.
- **Instabilité API LLM** : timeout + retry + fallback local.
- **Coût API** : déclenchement limité (tour 1 + tous les 10 tours).
- **Qualité conseils** : prompts stricts + format de sortie imposé.

## 8. Définition de Done (DoD)

Pour chaque US livrée :

- Code fonctionnel.
- Tests unitaires/intégration pertinents.
- Logs exploitables.
- Documentation mise à jour.
- Démonstration manuelle reproductible.

## 9. Pilotage autonome

- Avancer en **vertical slice** (de l’export à l’overlay).
- Pas de merge sans tests verts.
- Tracer les décisions techniques dans la documentation.
- Prioriser la stabilité avant le polish visuel.
