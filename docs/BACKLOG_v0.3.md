# BACKLOG MyTalleyrand v0.3

**Date de mise à jour :** 10 juillet 2026
**Version :** 0.3
**Sprint actuel :** Sprint P0 - Préparation partage communauté

> **Contexte du projet :** ce backlog v0.3 regroupe les tâches à exécuter avant de partager le dépôt MyTalleyrand à la communauté. Il s'appuie sur le backlog initial `docs/BACKLOG_v0.1.md` et sur le backlog de stabilisation `docs/BACKLOG_v0.2.md`, mais se concentre uniquement sur la mise à disposition publique : sécurité, onboarding, documentation, qualité de dépôt, contribution et support.

---

## Définitions de succès (jalons)

| Jalon | Définition | Portée |
| --- | --- | --- |
| **Repo publiable** | Le dépôt peut être rendu public sans secret, sans artefact local fragile et avec une licence claire. | Sprint P0 |
| **Installation reproductible** | Un utilisateur technique peut cloner, installer et lancer une recette minimale sans assistance directe. | Sprint P0-P1 |
| **Contribution communautaire** | Un contributeur peut comprendre le périmètre, lancer les tests et proposer une PR dans un cadre clair. | Sprint P1 |

**Contraintes actées :**
- Public cible initial : développeurs/players techniques sur macOS, pas distribution grand public.
- Aucun asset propriétaire Civ5/Firaxis ne doit être inclus.
- Les clés API et données locales utilisateur ne doivent jamais être versionnées.
- Les limitations macOS/Civ5/Steam doivent être visibles dès l'onboarding.
- La v0.3 ne remplace pas les backlogs v0.1/v0.2 : elle prépare le partage externe.

---

## Vue d'ensemble

| Métrique | Valeur |
| --- | --- |
| **Total User Stories** | 14 |
| **US Terminées** | 0 |
| **US En cours (partielles)** | 0 |
| **US À faire** | 14 |
| **US Won't** | 0 |
| **Progression** | 0/14 actives — 0% |

### Répartition par Epic

| Epic | US | Jalon dominant | Statut |
| --- | --- | --- | --- |
| EPIC 0 : Sécurité & hygiène du dépôt | 4 | Repo publiable | 📝 0/4 terminées |
| EPIC 1 : Documentation publique & onboarding | 4 | Installation reproductible | 📝 0/4 terminées |
| EPIC 2 : Validation, CI & qualité de contribution | 4 | Contribution communautaire | 📝 0/4 terminées |
| EPIC 3 : Publication & support communautaire | 2 | Contribution communautaire | 📝 0/2 terminées |

### Légende des statuts

- 📝 **À faire** · 🔄 **En cours** · ✅ **Terminé** · ⏸️ **En attente** · 🚫 **Abandonné**

### Légende MoSCoW

- 🔴 **Must** (bloquant pour un jalon) · 🟠 **Should** (fort impact, non bloquant) · 🟢 **Could** (confort) · ⚪ **Won't** (hors périmètre pour ce cycle)

---

## EPIC 0 : Sécurité & hygiène du dépôt

**Objectif :** Garantir que le dépôt peut être partagé sans secret, artefact local fragile, donnée personnelle ou ambiguïté de licence.
**Statut global :** 📝 0/4 terminées

---

### US-043 : Audit secrets et données sensibles avant publication

**Statut :** 📝 À faire · **Priorité :** 🔴 Must · **Jalon :** Repo publiable · **Sprint :** Sprint P0

**User Story :**
> En tant que **mainteneur**, je veux **scanner le dépôt avant publication**, afin de **ne partager aucune clé API, token, chemin privé sensible ou donnée utilisateur**.

#### Tâches techniques
- Scanner le dépôt complet avec au moins un outil ou script de détection de secrets.
- Vérifier spécifiquement `coach/.venv`, fichiers de configuration, logs, exemples, historique de docs et fixtures.
- Remplacer toute valeur sensible par des exemples neutres.
- Documenter les variables d'environnement et comptes Keychain attendus.

#### Critères d'acceptation
✅ Aucun secret détectable dans le worktree publié
✅ Les exemples de configuration utilisent uniquement des placeholders

#### Dépendances
- US-037 du backlog v0.2

---

### US-044 : Nettoyage des artefacts locaux versionnés

**Statut :** 📝 À faire · **Priorité :** 🔴 Must · **Jalon :** Repo publiable · **Sprint :** Sprint P0

**User Story :**
> En tant que **mainteneur**, je veux **retirer ou ignorer les artefacts locaux non reproductibles**, afin de **réduire le bruit du dépôt et éviter des installations cassées chez les contributeurs**.

#### Tâches techniques
- Décider du statut final de `coach/.venv`.
- Mettre à jour `.gitignore` pour venv, caches, logs, données utilisateur et exports locaux.
- Supprimer du suivi Git les artefacts qui doivent être générés localement.
- Vérifier que les scripts install/run recréent ce qui est nécessaire.

#### Critères d'acceptation
✅ Le dépôt public ne contient pas d'environnement local fragile
✅ Un clone propre peut recréer l'environnement documenté

#### Dépendances
- US-041 du backlog v0.2

---

### US-045 : Revue licence et attribution

**Statut :** 📝 À faire · **Priorité :** 🔴 Must · **Jalon :** Repo publiable · **Sprint :** Sprint P0

**User Story :**
> En tant que **mainteneur**, je veux **clarifier licence, attribution et absence d'assets propriétaires**, afin de **partager le projet sans ambiguïté juridique**.

#### Tâches techniques
- Vérifier `LICENSE` et son adéquation avec l'intention de partage.
- Ajouter une section "Non affiliation / assets Civ5" dans le README si nécessaire.
- Vérifier les licences des dépendances Python directes.
- S'assurer qu'aucune image, police ou donnée propriétaire Civ5/Firaxis n'est incluse.

#### Critères d'acceptation
✅ Licence visible et compréhensible
✅ Le README précise clairement que le projet n'est pas affilié à Firaxis/2K/Aspyr

#### Dépendances
- US-005 du backlog v0.1

---

### US-046 : Normalisation de la structure du dépôt public

**Statut :** 📝 À faire · **Priorité :** 🟠 Should · **Jalon :** Repo publiable · **Sprint :** Sprint P0

**User Story :**
> En tant que **nouveau contributeur**, je veux **une structure de dépôt lisible et cohérente**, afin de **comprendre rapidement où sont le mod, le coach, les docs et les scripts**.

#### Tâches techniques
- Vérifier les noms de dossiers et documents publics.
- Ajouter un court plan du dépôt dans le README.
- Archiver ou renommer les fichiers obsolètes.
- Vérifier que les backlogs versionnés sont expliqués.

#### Critères d'acceptation
✅ Le README explique la structure du dépôt
✅ Aucun fichier obsolète ne ressemble à la source de vérité actuelle

#### Dépendances
- Aucune

---

## EPIC 1 : Documentation publique & onboarding

**Objectif :** Permettre à un utilisateur technique de comprendre, installer, lancer et diagnostiquer MyTalleyrand sans assistance directe.
**Statut global :** 📝 0/4 terminées

---

### US-047 : README public orienté premier lancement

**Statut :** 📝 À faire · **Priorité :** 🔴 Must · **Jalon :** Installation reproductible · **Sprint :** Sprint P0

**User Story :**
> En tant qu'**utilisateur découvrant le projet**, je veux **un README qui explique clairement ce que fait MyTalleyrand et comment le tester**, afin de **savoir en quelques minutes si le projet est pour moi**.

#### Tâches techniques
- Ajouter une description courte du projet, de ses limites et du public cible.
- Mettre en avant macOS, Civ5 Steam et mode fenêtré.
- Fournir un "quick start" depuis clone propre.
- Ajouter une section troubleshooting courte avec liens vers docs détaillées.

#### Critères d'acceptation
✅ Un nouveau lecteur comprend le projet et ses limites en moins de 5 minutes
✅ Le premier lancement est décrit sans supposer de contexte privé

#### Dépendances
- US-029 du backlog v0.2

---

### US-048 : Guide d'installation communautaire macOS

**Statut :** 📝 À faire · **Priorité :** 🔴 Must · **Jalon :** Installation reproductible · **Sprint :** Sprint P0

**User Story :**
> En tant qu'**utilisateur macOS**, je veux **un guide d'installation complet et à jour**, afin de **configurer Civ5, le mod, le coach et les clés API sans assistance**.

#### Tâches techniques
- Revalider `docs/MACOS_GUIDE.md` après US-028.
- Documenter chemins Steam/Aspyr/Library et base `ModUserData`.
- Documenter Keychain, Mistral/OpenAI, permissions Accessibilité et mode fenêtré.
- Ajouter une procédure de désinstallation.

#### Critères d'acceptation
✅ Installation réalisable depuis clone propre en suivant le guide
✅ Les erreurs connues ont une section de diagnostic

#### Dépendances
- US-028, US-030 du backlog v0.2

---

### US-049 : Documentation de recette sans Civ5

**Statut :** 📝 À faire · **Priorité :** 🟠 Should · **Jalon :** Installation reproductible · **Sprint :** Sprint P1

**User Story :**
> En tant que **contributeur sans partie Civ5 prête**, je veux **pouvoir tester le coach avec des fixtures**, afin de **valider une contribution sans relancer une vraie partie**.

#### Tâches techniques
- Documenter le replay de fixtures SQLite/JSON.
- Fournir au moins une fixture publique sans donnée privée.
- Décrire les commandes de validation rapide.

#### Critères d'acceptation
✅ Un contributeur peut tester le pipeline coach sans Civ5
✅ La fixture publique ne contient aucune donnée sensible

#### Dépendances
- US-038 du backlog v0.2

---

### US-050 : Captures et démonstration non propriétaires

**Statut :** 📝 À faire · **Priorité :** 🟢 Could · **Jalon :** Installation reproductible · **Sprint :** Sprint P1

**User Story :**
> En tant que **visiteur du repo**, je veux **voir une démonstration de l'overlay et du flux coach sans asset propriétaire**, afin de **comprendre l'expérience utilisateur avant installation**.

#### Tâches techniques
- Produire des captures de l'overlay sans contenu Civ5 propriétaire visible.
- Ajouter une courte démonstration textuelle ou GIF si légalement sûr.
- Vérifier que les images ne révèlent pas de clé, chemin privé ou donnée utilisateur.

#### Critères d'acceptation
✅ Le README illustre l'expérience sans risque d'asset propriétaire

#### Dépendances
- US-005 du backlog v0.1, US-023 du backlog v0.2

---

## EPIC 2 : Validation, CI & qualité de contribution

**Objectif :** Donner aux contributeurs des garde-fous simples pour tester, modifier et proposer des changements fiables.
**Statut global :** 📝 0/4 terminées

---

### US-051 : CI publique minimale

**Statut :** 📝 À faire · **Priorité :** 🔴 Must · **Jalon :** Contribution communautaire · **Sprint :** Sprint P0

**User Story :**
> En tant que **contributeur**, je veux **voir les validations automatiques sur chaque PR**, afin de **savoir rapidement si ma contribution casse le projet**.

#### Tâches techniques
- Ajouter GitHub Actions pour tests Python et `scripts/validate.sh`.
- Vérifier modinfo/XML et fichiers requis.
- Documenter la compatibilité macOS vs exécution CI Linux si applicable.

#### Critères d'acceptation
✅ Une PR déclenche les validations de base
✅ Les échecs sont compréhensibles

#### Dépendances
- US-042 du backlog v0.2

---

### US-052 : Guide de contribution

**Statut :** 📝 À faire · **Priorité :** 🟠 Should · **Jalon :** Contribution communautaire · **Sprint :** Sprint P1

**User Story :**
> En tant que **contributeur**, je veux **un guide de contribution court**, afin de **savoir comment proposer une issue, une PR, un test ou une amélioration de prompt**.

#### Tâches techniques
- Ajouter `CONTRIBUTING.md`.
- Décrire installation dev, tests, style attendu et séparation mod/coach/docs.
- Expliquer comment manipuler les clés API sans les committer.

#### Critères d'acceptation
✅ Un contributeur sait lancer les tests et ouvrir une PR

#### Dépendances
- US-051

---

### US-053 : Templates issues et pull requests

**Statut :** 📝 À faire · **Priorité :** 🟠 Should · **Jalon :** Contribution communautaire · **Sprint :** Sprint P1

**User Story :**
> En tant que **mainteneur**, je veux **des templates d'issues et de PR**, afin de **recevoir des signalements exploitables sans multiplier les allers-retours**.

#### Tâches techniques
- Ajouter templates bug, demande de feature et PR.
- Inclure version macOS, version Civ5, provider LLM, logs utiles et étapes de reproduction.
- Ajouter une checklist sécurité : pas de clé API, pas de logs privés.

#### Critères d'acceptation
✅ Les nouvelles issues guident vers les informations utiles

#### Dépendances
- US-052

---

### US-054 : Politique de sécurité légère

**Statut :** 📝 À faire · **Priorité :** 🟠 Should · **Jalon :** Contribution communautaire · **Sprint :** Sprint P1

**User Story :**
> En tant que **utilisateur ou contributeur**, je veux **savoir comment signaler un problème de sécurité**, afin de **ne pas publier accidentellement une clé ou une vulnérabilité dans une issue publique**.

#### Tâches techniques
- Ajouter `SECURITY.md`.
- Décrire le traitement attendu des secrets/API keys/logs.
- Indiquer un canal de contact ou une procédure temporaire.

#### Critères d'acceptation
✅ Le repo explique comment signaler un problème sensible

#### Dépendances
- US-043

---

## EPIC 3 : Publication & support communautaire

**Objectif :** Publier le projet avec un cadre clair et une première boucle de support réaliste.
**Statut global :** 📝 0/2 terminées

---

### US-055 : Préparation de la première release publique

**Statut :** 📝 À faire · **Priorité :** 🟠 Should · **Jalon :** Contribution communautaire · **Sprint :** Sprint P1

**User Story :**
> En tant que **mainteneur**, je veux **publier une première release lisible**, afin de **donner un point de départ stable à la communauté**.

#### Tâches techniques
- Rédiger notes de release : fonctionnalités, limites, installation, risques connus.
- Tagger une version après validation.
- Lister explicitement ce qui est expérimental.

#### Critères d'acceptation
✅ Une release publique décrit clairement ce qui marche et ce qui reste expérimental

#### Dépendances
- US-047, US-048, US-051

---

### US-056 : Roadmap publique et règles de support

**Statut :** 📝 À faire · **Priorité :** 🟢 Could · **Jalon :** Contribution communautaire · **Sprint :** Sprint P1

**User Story :**
> En tant que **utilisateur intéressé**, je veux **comprendre la roadmap et le niveau de support attendu**, afin de **savoir si je peux m'appuyer sur le projet ou contribuer**.

#### Tâches techniques
- Résumer les backlogs v0.1/v0.2/v0.3 dans une roadmap publique.
- Définir ce qui est supporté : macOS, Civ5 Steam, providers LLM.
- Définir ce qui n'est pas supporté pour le moment : Windows, packaging grand public, assets propriétaires.

#### Critères d'acceptation
✅ La roadmap publique évite les attentes irréalistes

#### Dépendances
- US-055

---

## Roadmap & Sprints (mise à jour)

### Sprint P0 : Repo publiable
| US |
| --- |
| US-043, US-044, US-045, US-046, US-047, US-048, US-051 |

**Critère de sortie :** le dépôt peut être rendu public sans secret, avec licence claire, README public, guide macOS et CI minimale.

### Sprint P1 : Contribution communautaire
| US |
| --- |
| US-049, US-050, US-052, US-053, US-054, US-055, US-056 |

**Critère de sortie :** un contributeur peut tester sans Civ5, proposer une PR cadrée, signaler un bug correctement et comprendre la roadmap.

---

## Stack et politiques publiques

| Sujet | Décision | Justification |
| --- | --- | --- |
| **Plateforme supportée** | macOS uniquement au lancement public | C'est le seul environnement testé |
| **Providers LLM** | Mistral par défaut, OpenAI alternatif | Aligné v0.2 |
| **Assets propriétaires** | Aucun asset Civ5/Firaxis | Réduction du risque juridique |
| **Secrets** | Keychain/env vars, jamais Git | Sécurité utilisateur |
| **Contributions** | PR avec tests/validation | Maintenabilité |

---

## Risques & Mitigations

| Risque | Probabilité | Impact | Mitigation |
| --- | --- | --- | --- |
| Secret committé avant publication | Moyen | Haut | US-043 + SECURITY.md |
| Installation trop fragile pour tiers | Moyen | Haut | US-047 + US-048 + US-049 |
| `.venv` pollue le dépôt public | Élevé | Moyen | US-044 + US-041 v0.2 |
| Ambiguïté juridique Civ5/Firaxis | Faible | Haut | US-045 + US-050 |
| Contributions difficiles à trier | Moyen | Moyen | US-052 + US-053 + US-051 |

---

## Notes de mise à jour

**10 juillet 2026 (création v0.3 partage communauté)**
- Ajout du backlog dédié à la publication communautaire
- Couverture sécurité, documentation, CI, contribution, release et support

---

**Prochaine revue de backlog :** après stabilisation v0.2 R0/R1, avant ouverture publique du dépôt
