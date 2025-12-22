# Backlog & Précadrage technique

## BACKLOG
EPIC 1 : Fondations techniques 🔴 Critique
US-001 : Collecte de données de jeu
En tant que mod
Je veux exporter l'état du jeu dans un format structuré
Afin que l'application externe puisse l'analyser

Tâches :

 Créer fonction CollectGameState() en Lua
 Extraire paramètres de partie (difficulté, taille, civ)
 Extraire état du joueur (ressources, villes, unités)
 Extraire relations diplomatiques
 Exporter en JSON dans dossier accessible
 Gérer les erreurs d'écriture fichier
Critères d'acceptation :

Fichier JSON généré à chaque tour
Toutes les données nécessaires présentes
Format validé (JSON valid)
Performance < 100ms par export
Estimation : 5 points
Priorité : P0 (Bloquant)

US-002 : Application coach externe - Squelette
En tant qu' utilisateur
Je veux une application qui tourne en arrière-plan
Afin de recevoir des conseils pendant ma partie

Tâches :

 Choisir stack technique (Python + Flask ou Electron + Node)
 Créer projet avec structure modulaire
 Implémenter lecture fichier gamestate.json
 Créer système de polling (check nouveau tour)
 Logger les états de jeu détectés
Critères d'acceptation :

Application démarre sans erreur
Détecte nouveaux états de jeu en < 2s
Logs clairs et debuggables
Estimation : 8 points
Priorité : P0 (Bloquant)

US-003 : Intégration API LLM
En tant que coach
Je veux envoyer l'état du jeu à un LLM
Afin d' obtenir des recommandations stratégiques

Tâches :

 Choisir provider LLM (OpenAI, Anthropic, local)
 Créer module d'appel API
 Définir prompt système pour le coach
 Structurer les requêtes (état → prompt)
 Parser les réponses du LLM
 Gérer retry et erreurs réseau
 Implémenter rate limiting
Critères d'acceptation :

Appel API réussi avec gamestate
Réponse parsée et structurée
Gestion des erreurs (timeout, quota)
Temps de réponse < 10s
Estimation : 8 points
Priorité : P0 (Bloquant)

EPIC 2 : Interface utilisateur 🟠 Important
US-004 : Overlay de base
En tant qu' utilisateur
Je veux voir les conseils du coach superposés sur le jeu
Afin de ne pas avoir à alt-tab

Tâches :

 Créer fenêtre overlay transparente
 Détecter position de la fenêtre Civ5
 Afficher texte par-dessus le jeu
 Rendre l'overlay cliquable/déplaçable
 Gérer multi-écrans
Critères d'acceptation :

Overlay visible sur Civ5
Transparent sauf zone de texte
Ne bloque pas les clics sur le jeu
Position persistante
Estimation : 13 points
Priorité : P1

US-005 : Interface style conseiller Civ5
En tant qu' utilisateur
Je veux une UI qui ressemble aux conseillers natifs
Afin d' avoir une expérience cohérente

Tâches :

 Analyser les assets des conseillers Civ5
 Créer mockups de l'interface
 Implémenter design (CSS/Qt selon stack)
 Ajouter portrait de Talleyrand
 Animer l'apparition des conseils
 Ajouter boutons (fermer, réduire, historique)
Critères d'acceptation :

Ressemble aux conseillers natifs
Responsive et lisible
Animations fluides
Boutons fonctionnels
Estimation : 13 points
Priorité : P2

EPIC 3 : Logique du coach 🟡 Normal
US-006 : Dialogue d'initialisation (Tour 1)
En tant que joueur
Je veux indiquer ma stratégie de victoire au tour 1
Afin que le coach adapte ses conseils

Tâches :

 Créer popup au tour 1 dans l'overlay
 Proposer choix de victoire (domination, science, culture, diplo)
 Détecter automatiquement paramètres de partie
 Sauvegarder les préférences du joueur
 Envoyer ces infos au LLM pour contexte
Critères d'acceptation :

Popup s'affiche au tour 1 uniquement
Tous les types de victoire proposés
Détection auto des paramètres fonctionne
Préférences sauvegardées
Estimation : 5 points
Priorité : P1

US-007 : Analyse cyclique (tous les 10 tours)
En tant que coach
Je veux analyser la partie tous les 10 tours
Afin de proposer un objectif à 10 tours

Tâches :

 Implémenter déclencheur tous les 10 tours
 Créer prompt "analyse de situation"
 Demander au LLM un objectif pour 10 prochains tours
 Afficher l'objectif dans l'overlay
 Sauvegarder historique des objectifs
Critères d'acceptation :

Analyse tous les 10 tours exactement
Objectif clair et actionnable
Affiché dans l'UI
Historique accessible
Estimation : 8 points
Priorité : P1

US-008 : Recommandations d'actions
En tant que joueur
Je veux recevoir des actions concrètes à effectuer
Afin de progresser vers mon objectif

Tâches :

 Créer prompt "recommandations d'actions"
 Demander au LLM : constructions prioritaires
 Demander technologies à rechercher
 Demander doctrines sociales
 Demander actions militaires (unités, positionnement)
 Structurer réponse LLM (liste d'actions)
 Afficher actions dans l'UI (checklist)
Critères d'acceptation :

Au moins 3-5 actions par analyse
Actions claires et réalisables
Catégorisées (construction, science, militaire)
Affichées de manière lisible
Estimation : 13 points
Priorité : P1

EPIC 4 : Optimisation et polish 🟢 Nice to have
US-009 : Cache et optimisation LLM
En tant que développeur
Je veux optimiser les appels LLM
Afin de réduire coûts et latence

Tâches :

 Implémenter cache des réponses similaires
 Détecter changements mineurs (pas de réanalyse)
 Utiliser modèle plus léger pour pré-analyse
 Batch requests si possible
Estimation : 5 points
Priorité : P3

US-010 : Historique des conseils
En tant que joueur
Je veux consulter les conseils passés
Afin de revoir ma stratégie

Tâches :

 Sauvegarder tous les conseils dans base locale
 Créer interface d'historique
 Filtrer par tour/catégorie
 Export en texte/PDF
Estimation : 8 points
Priorité : P3

US-011 : Configuration avancée
En tant qu' utilisateur avancé
Je veux configurer le comportement du coach
Afin de personnaliser l'expérience

Tâches :

 Interface de settings
 Fréquence d'analyse (5/10/20 tours)
 Niveau de détail (débutant/expert)
 Choix du modèle LLM
 Désactiver certains types de conseils
Estimation : 8 points
Priorité : P3

US-012 : Mode hors-ligne avec LLM local
En tant qu' utilisateur sans connexion
Je veux utiliser un LLM local
Afin de jouer hors-ligne

Tâches :

 Intégrer Ollama ou LlamaCpp
 Télécharger modèle optimisé
 Adapter prompts pour modèle local
 Interface de switch online/offline
Estimation : 13 points
Priorité : P4

EPIC 5 : Documentation et tests 🔵 Essentiel
US-013 : Documentation utilisateur
Tâches :

 README avec installation détaillée
 Guide de configuration LLM API
 Troubleshooting
 Vidéo de démonstration
Estimation : 5 points
Priorité : P1

US-014 : Tests et validation
Tâches :

 Tests unitaires (modules Python/Node)
 Tests d'intégration (mod + app)
 Tests en partie réelle (10+ tours)
 Validation performance
Estimation : 13 points
Priorité : P2

📊 SYNTHÈSE DU BACKLOG
Roadmap suggérée
Sprint 0 (2-3 semaines) - MVP Technique

US-001 : Collecte données ✅
US-002 : App coach squelette ✅
US-003 : Intégration LLM ✅
Sprint 1 (2 semaines) - Interface de base

US-004 : Overlay de base ✅
US-006 : Dialogue tour 1 ✅
Sprint 2 (2-3 semaines) - Logique coach

US-007 : Analyse cyclique ✅
US-008 : Recommandations d'actions ✅
Sprint 3 (1-2 semaines) - Polish MVP

US-005 : Interface style Civ5 ✅
US-013 : Documentation ✅
Sprint 4+ - Améliorations

US-009 à US-012 (optimisations)
US-014 : Tests complets

## CHOIX TECHNIQUES RECOMMANDÉS

Stack Application Coach

## Option A : Python (Recommandée pour MVP)
- Python 3.10+
- Flask (API interne)
- Tkinter ou PyQt6 (Overlay UI)
- OpenAI SDK ou Anthropic SDK
- watchdog (file monitoring)

## Option B : Electron + Node
- Electron (Overlay riche)
- Express (API)
- React (UI moderne)
- Axios (LLM API calls)
- Chokidar (file watching)

Architecture finale
┌──────────────────┐
│  Civilization V  │
│   + Mod Lua      │
│                  │
│  Exporte état → │ gamestate.json
└──────────────────┘         ↓
                    ┌─────────────────┐
                    │  Coach App      │
                    │  (Python/Node)  │
                    │                 │
                    │  1. Lit JSON    │
                    │  2. Analyse LLM │
                    │  3. Affiche UI  │
                    └─────────────────┘
                             ↓
                    ┌─────────────────┐
                    │  Overlay UI     │
                    │  (sur Civ5)     │
                    │                 │
                    │  • Objectifs    │
                    │  • Actions      │
                    │  • Conseils     │
                    └─────────────────┘


## VERDICT DE FAISABILITÉ

Aspect	Faisabilité	Notes
Concept général	✅ Faisable	Avec architecture hybride
Intégration Civ5	⚠️ Limitée	Mod = export données uniquement
Appel LLM	✅ Faisable	Via app externe
Overlay UI	✅ Faisable	Technologie mature
Expérience utilisateur	⚠️ Acceptable	Moins intégré qu'un vrai mod
Complexité technique	🟡 Moyenne	2 composants à maintenir
Coût LLM	⚠️ Variable	Dépend usage, prévoir budget
Conclusion : ✅ Projet FAISABLE avec l'architecture hybride proposée.

Le projet est ambitieux mais réalisable. La limitation principale (pas de réseau dans Civ5) est contournable via une application externe. L'expérience utilisateur sera bonne si l'overlay est bien conçu.