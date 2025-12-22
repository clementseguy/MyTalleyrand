# 📜 MyTalleyrand - README du Mod

Mod Civilization V avec intégration LLM pour coaching stratégique en temps réel.

## 📦 Structure

```
mod/
├── MyTalleyrand.modinfo   # Configuration du mod
├── XML/                   # Définitions de jeu
│   ├── GameDefines.xml
│   └── Text.xml
├── Lua/                   # Scripts de gameplay
│   └── GameplayScript.lua
├── SQL/                   # Modifications BDD
│   └── ModSchema.sql
└── Art/                   # Assets graphiques
```

## 🎯 Fonctionnalités

- Export de l'état du jeu au format JSON à chaque tour
- Détection automatique des décisions stratégiques
- Compatible avec toutes les versions de Civilization V (Vanilla, G&K, BNW)

## 📥 Installation

### macOS (Aspyr)

```bash
# Copier le mod dans le dossier approprié
cp -r mod/ ~/Documents/Aspyr/Sid\ Meier\'s\ Civilization\ 5/MODS/MyTalleyrand/

# Créer le dossier d'export
mkdir -p ~/Documents/Aspyr/Sid\ Meier\'s\ Civilization\ 5/MODS/MyTalleyrand/export/
```

### Windows (Steam)

```bash
# Copier le mod
xcopy /E /I mod "%USERPROFILE%\Documents\My Games\Sid Meier's Civilization 5\MODS\MyTalleyrand\"

# Créer le dossier d'export
mkdir "%USERPROFILE%\Documents\My Games\Sid Meier's Civilization 5\MODS\MyTalleyrand\export"
```

## 🚀 Activation

1. Lancer Civilization V
2. Menu principal → **Mods**
3. Cocher **MyTalleyrand**
4. **Next**
5. Démarrer une nouvelle partie ou charger une sauvegarde

## 📤 Export de données

Le mod exporte automatiquement l'état du jeu dans :

```
~/Documents/Aspyr/Sid Meier's Civilization 5/MODS/MyTalleyrand/export/gamestate.json
```

### Format JSON

```json
{
  "turn": 42,
  "player": {
    "civilization": "CIVILIZATION_FRANCE",
    "leader": "LEADER_NAPOLEON",
    "gold": 350,
    "science": 120,
    "culture": 85
  },
  "cities": [...],
  "units": [...],
  "diplomacy": {...}
}
```

## 🔍 Debugging

### Logs du mod

```bash
# macOS
tail -f ~/Documents/Aspyr/Sid\ Meier\'s\ Civilization\ 5/Logs/Lua.log

# Windows
type "%USERPROFILE%\Documents\My Games\Sid Meier's Civilization 5\Logs\Lua.log"
```

### Vérifier l'export

```bash
# macOS
cat ~/Documents/Aspyr/Sid\ Meier\'s\ Civilization\ 5/MODS/MyTalleyrand/export/gamestate.json

# Surveiller les mises à jour
watch -n 1 cat .../export/gamestate.json
```

## 🛠️ Développement

### Modifier le mod

1. Éditer les fichiers dans `mod/`
2. Relancer Civilization V
3. Charger une partie pour tester

### Validation

```bash
# Depuis la racine du repo
./scripts/validate.sh
```

## 📚 Documentation complète

- [Architecture technique](../docs/SUMMARY.md)
- [Guide de test](../docs/TESTING.md)
- [Backlog](../docs/BACKLOG.md)

## ⚠️ Limitations

- Pas de support réseau direct (Lua Civ5 limité)
- Export JSON uniquement au début de chaque tour
- Compatible mode solo uniquement (pas de multijoueur)

## 🤝 Contribution

Voir [BACKLOG.md](../docs/BACKLOG.md) pour les User Stories en cours.

---

**Version :** 0.1.0  
**Auteur :** Clément Séguy  
**Licence :** À définir
