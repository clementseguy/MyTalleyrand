# Quickstart MyTalleyrand

## Installation (macOS)

```bash
./script/install_macos.sh
```

## Configuration coach

Éditer le fichier :

```bash
~/Library/Application\ Support/MyTalleyrand/coach.user.json
```

Renseigner au minimum `llm.api_key`.

## Lancer le coach

```bash
cd ~/Applications/MyTalleyrandCoach/coach
.venv/bin/python src/main.py
```

## Vérification projet

```bash
./scripts/validate.sh
```
