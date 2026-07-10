# Mod MyTalleyrand (Civilization V)

Le mod exporte un état de jeu JSON consommé par le coach Python.

## Installation (macOS Steam / Aspyr)

### Option recommandée

```bash
./scripts/install_macos.sh
```

### Option manuelle

Sur la version **Steam/Aspyr macOS**, le jeu lit ses mods depuis le dossier de
données `~/Library/Application Support/Sid Meier's Civilization 5/` (qu'il voit en
interne comme `C:\Emu\AppDataParent\…` via l'émulation Windows) :

```bash
DEST=~/Library/Application\ Support/Sid\ Meier\'s\ Civilization\ 5/MODS/MyTalleyrand
mkdir -p "$DEST"
cp -R mod/. "$DEST/"
```

## Export gamestate

Sur macOS, le contexte Lua du mod (`InGameUIAddin`) **n'a pas accès à `io`/`os`**
(même avec `EnableLuaDebugLibrary = 1`) : écrire un fichier est impossible. Le mod
persiste donc l'état de partie dans sa base **`Modding.OpenUserData()`** (SQLite) :

- Base : `~/Library/Application Support/Sid Meier's Civilization 5/ModUserData/a1b2c3d4-e5f6-7890-abcd-ef1234567890-1.db`
- Table : `SimpleValues(Name TEXT PRIMARY KEY, Value VARIANT)`
- Clés écrites : `gamestate_json` (le JSON complet), `turn_number`, `write_seq`, `schema_version`

Écriture déclenchée à chaque début de tour du **joueur actif**
(`Events.ActivePlayerTurnStart`). Le coach lit cette base en lecture seule.

Le packaging du mod repose sur des contraintes spécifiques à ce build (format du
`.modinfo`, point d'entrée `InGameUIAddin` vers un `.xml`, purge du cache). Voir
[docs/MACOS_GUIDE.md](../docs/MACOS_GUIDE.md#mod-civ5--packaging-et-debug-macosaspyr).

### Format actuellement exporté

```json
{
  "schema_version": "0.1.0",
  "turn_id": 42,
  "turn_number": 42,
  "timestamp_utc": "2026-01-01T12:00:00Z",
  "game_parameters": {
    "difficulty": "HANDICAP_KING",
    "map_size": "WORLDSIZE_STANDARD",
    "game_speed": "GAMESPEED_STANDARD"
  },
  "player": {
    "id": 0,
    "civilization": "CIVILIZATION_FRANCE",
    "leader": "LEADER_NAPOLEON"
  },
  "resources": {
    "gold": 350,
    "science": 120
  },
  "cities": [
    {"id": 1, "name": "Paris", "population": 3, "production": "Monument"}
  ],
  "units": [
    {"id": 1, "type": "UNIT_WARRIOR", "x": 12, "y": 8, "moves": 2}
  ]
}
```

## Compatibilité coach

Le schéma attendu est défini dans `coach/config/gamestate.schema.v0.json`.
La version actuelle (`0.1.0`) est alignée entre le mod et le coach.

## Debug rapide

```bash
CIV="$HOME/Library/Application Support/Sid Meier's Civilization 5"

# Traces d'exécution du mod (nécessite LoggingEnabled=1 dans config.ini)
grep -i talleyrand "$CIV/Logs/Lua.log"

# Contenu exporté par le mod (base SQLite ModUserData)
sqlite3 "$CIV/ModUserData/a1b2c3d4-e5f6-7890-abcd-ef1234567890-1.db" \
  "SELECT Name, substr(CAST(Value AS TEXT),1,200) FROM SimpleValues;"
```

Procédure complète (activation des logs, purge du cache, format `.modinfo`) :
[docs/MACOS_GUIDE.md](../docs/MACOS_GUIDE.md#mod-civ5--packaging-et-debug-macosaspyr).
