# Mod MyTalleyrand (Civilization V)

Le mod exporte un état de jeu JSON consommé par le coach Python.

## Installation (macOS Aspyr / Steam)

### Option recommandée

```bash
./script/install_macos.sh
```

### Option manuelle

```bash
mkdir -p ~/Documents/Aspyr/Sid\ Meier\'s\ Civilization\ 5/MODS/MyTalleyrand
cp -R mod/. ~/Documents/Aspyr/Sid\ Meier\'s\ Civilization\ 5/MODS/MyTalleyrand/
mkdir -p ~/Documents/Aspyr/Sid\ Meier\'s\ Civilization\ 5/MODS/MyTalleyrand/export
```

## Export gamestate

Le script Lua écrit de manière atomique :

- Temporaire : `export/gamestate.tmp.json`
- Final : `export/gamestate.json`

Écriture déclenchée à chaque tour du **joueur actif**.

### Format actuellement exporté

```json
{
  "schema_version": "0.1.0",
  "turn_id": 42,
  "turn_number": 42,
  "timestamp_utc": "2026-01-01T12:00:00Z",
  "player": {
    "id": 0,
    "civilization": "CIVILIZATION_FRANCE",
    "leader": "LEADER_NAPOLEON"
  },
  "resources": {
    "gold": 350,
    "science": 120
  }
}
```

## Compatibilité coach

Le schéma attendu est défini dans `coach/config/gamestate.schema.v0.json`.
La version actuelle (`0.1.0`) est alignée entre le mod et le coach.

## Debug rapide

```bash
tail -f ~/Documents/Aspyr/Sid\ Meier\'s\ Civilization\ 5/Logs/Lua.log
cat ~/Documents/Aspyr/Sid\ Meier\'s\ Civilization\ 5/MODS/MyTalleyrand/export/gamestate.json
```
