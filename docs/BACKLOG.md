# Backlog MyTalleyrand

## Statut des User Stories

| US | Titre | Epic | Pts | Statut | Implémentation |
|----|-------|------|-----|--------|----------------|
| US-001 | Collecte données de jeu | Fondations | 5 | ✅ | `mod/Lua/GameplayScript.lua` — export atomique JSON |
| US-002 | Application coach squelette | Fondations | 8 | ✅ | `coach/src/` — structure modulaire Python |
| US-003 | Intégration API LLM | Fondations | 8 | ✅ | `coach/src/llm_client.py` — OpenAI + retry + fallback |
| US-004 | Overlay de base | Interface | 13 | ✅ | `coach/src/overlay.py` — abstraction testable |
| US-005 | Interface style conseiller Civ5 | Interface | 13 | 📝 | — |
| US-006 | Dialogue d'initialisation (Tour 1) | Coach | 5 | ✅ | `coach/src/coach.py` + `--victory-focus` CLI |
| US-007 | Analyse cyclique (tous les 10 tours) | Coach | 8 | ✅ | `coach/src/coach.py` — `turn_number % 10` |
| US-008 | Recommandations d'actions | Coach | 13 | ✅ | `LLMAdvice` — actions, catégories, risques |
| US-009 | Cache et optimisation LLM | Optim. | 5 | 📝 | — |
| US-010 | Historique des conseils | Optim. | 8 | 📝 | — |
| US-011 | Configuration avancée | Optim. | 8 | 📝 | — |
| US-012 | Mode hors-ligne LLM local | Optim. | 13 | 📝 | — |
| US-013 | Documentation utilisateur | Doc | 5 | ✅ | README.md, docs/, guides |
| US-014 | Tests et validation | Doc | 13 | ✅ | 7 fichiers pytest, validate.sh |

**Progression :** 9/14 US terminées (64%) — 81/115 points

## Travail restant

### US-005 : Interface style conseiller Civ5 (P2, 13 pts)

Remplacer l'overlay abstrait par une vraie UI PyQt6 :
- Fenêtre transparente toujours au-dessus (mode fenêtré requis)
- Design inspiré des conseillers natifs Civ5
- Portrait de Talleyrand, animations, boutons (fermer, historique)

### US-009 : Cache et optimisation LLM (P3, 5 pts)

- Cache des réponses pour situations similaires
- Détection de changements mineurs (skip réanalyse)

### US-010 : Historique consultable (P3, 8 pts)

- Interface de consultation des conseils passés
- Filtrage par tour/catégorie
- Note : un historique JSON brut existe déjà (`coach_history.json`)

### US-011 : Configuration avancée (P3, 8 pts)

- Interface de settings
- Fréquence d'analyse configurable (5/10/20 tours)
- Niveau de détail (débutant/expert)

### US-012 : Mode hors-ligne avec LLM local (P4, 13 pts)

- Intégrer Ollama ou LlamaCpp
- Adapter les prompts pour modèles locaux
- Interface de switch online/offline

## Améliorations techniques non planifiées

- Intégration Keychain réelle (`keyring`) — remplacer les stubs `NotImplementedError` dans `keychain.py`
- Migration watcher vers `watchdog` (FSEvents natif macOS)
- Enrichissement du schéma gamestate (villes, diplomatie, technologies)
- Packaging macOS (.app, code signing, notarization)
- Support multi-provider LLM (Anthropic, Google)
