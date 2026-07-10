# Audit du `.venv` de debug

## Décision R0

Le dossier `coach/.venv` est conservé temporairement pour ne pas perdre l'environnement de debug fonctionnel utilisé pendant la recette. Il n'est pas reconstruit dans ce sprint.

## Audit réalisé

Commande :

```bash
./scripts/audit_debug_venv.sh
```

Résultat R0 : aucun secret détectable par les motifs connus.

Le scan cherche des valeurs concrètes de clés/tokens, notamment clés OpenAI `sk-...`, en-têtes `Bearer ...` et affectations explicites de variables d'environnement API. Il ignore les simples noms de variables présents dans les bibliothèques installées.

## Nettoyage futur

Une tâche dédiée (`US-041`) devra décider de la sortie normale du `.venv` du versionnement, ajouter/corriger `.gitignore`, documenter la recréation reproductible et supprimer les diffs d'environnement non portables.
