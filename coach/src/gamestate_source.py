"""Sources de gamestate : fichier JSON (legacy/Windows) ou base SQLite ModUserData (macOS).

Sur macOS (Civ5 Steam/Aspyr, émulation Windows), le contexte Lua du mod n'a ni `io`
ni `os.execute` : il ne peut pas écrire de fichier. Le mod persiste donc l'état de
partie dans sa base `Modding.OpenUserData()` (SQLite) — table
`SimpleValues(Name, Value)` — que ce module lit en lecture seule.
"""

from __future__ import annotations

import logging
import sqlite3
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

logger = logging.getLogger(__name__)

# Clé de la table SimpleValues contenant le JSON d'état de partie (écrite par le mod).
GAMESTATE_KEY = "gamestate_json"


@dataclass(frozen=True)
class SourceSnapshot:
    """Résultat d'une lecture de source.

    - exists: la source (fichier / base) est présente.
    - change_token: identifiant de version du contenu (mtime, write_seq…). None si absent.
    - raw_json: le JSON de gamestate courant, ou None si indisponible/inchangé.
    """

    exists: bool
    change_token: int | None
    raw_json: str | None


class GameStateSource(Protocol):
    """Interface d'une source de gamestate."""

    @property
    def label(self) -> str:
        """Chemin lisible pour les logs et messages d'erreur."""

    def read(self) -> SourceSnapshot:
        """Lit l'état courant de la source (appel bon marché, tolérant aux erreurs)."""


class FileGameStateSource:
    """Source historique : un fichier gamestate.json écrit par le mod (Windows)."""

    def __init__(self, path: Path):
        self._path = Path(path)

    @property
    def label(self) -> str:
        return str(self._path)

    def read(self) -> SourceSnapshot:
        if not self._path.exists():
            return SourceSnapshot(exists=False, change_token=None, raw_json=None)
        try:
            mtime = self._path.stat().st_mtime_ns
            raw = self._path.read_text(encoding="utf-8")
        except OSError as exc:
            logger.warning("Lecture du fichier gamestate impossible (%s): %s", self._path, exc)
            return SourceSnapshot(exists=True, change_token=None, raw_json=None)
        return SourceSnapshot(exists=True, change_token=mtime, raw_json=raw)


class SqliteModUserDataSource:
    """Source macOS : base SQLite ModUserData écrite par le mod via Modding.OpenUserData.

    Lecture en mode read-only pour cohabiter avec le jeu qui garde la base ouverte.
    Le jeton de changement est `write_seq` (incrémenté par le mod à chaque tour),
    avec repli sur le mtime du fichier si la clé n'est pas encore présente.
    """

    def __init__(self, db_path: Path, busy_timeout_seconds: float = 1.0):
        self._path = Path(db_path)
        self._busy_timeout_seconds = busy_timeout_seconds

    @property
    def label(self) -> str:
        return str(self._path)

    def _connect(self) -> sqlite3.Connection:
        # mode=ro : n'échoue pas si le jeu détient la base ; ne crée jamais le fichier.
        uri = f"file:{self._path.as_posix()}?mode=ro"
        conn = sqlite3.connect(uri, uri=True, timeout=self._busy_timeout_seconds)
        conn.execute(f"PRAGMA busy_timeout = {int(self._busy_timeout_seconds * 1000)}")
        return conn

    def read(self) -> SourceSnapshot:
        if not self._path.exists():
            return SourceSnapshot(exists=False, change_token=None, raw_json=None)

        try:
            conn = self._connect()
        except sqlite3.Error as exc:
            logger.debug("Ouverture SQLite ModUserData impossible (%s): %s", self._path, exc)
            return SourceSnapshot(exists=True, change_token=None, raw_json=None)

        try:
            values = self._read_values(conn)
        except sqlite3.OperationalError as exc:
            # Base verrouillée ou en cours d'écriture : on réessaiera au prochain poll.
            logger.debug("SQLite ModUserData temporairement indisponible (%s): %s", self._path, exc)
            return SourceSnapshot(exists=True, change_token=None, raw_json=None)
        except sqlite3.Error as exc:
            logger.warning("Lecture SQLite ModUserData échouée (%s): %s", self._path, exc)
            return SourceSnapshot(exists=True, change_token=None, raw_json=None)
        finally:
            conn.close()

        raw_json = values.get(GAMESTATE_KEY)
        if raw_json is not None and not isinstance(raw_json, str):
            raw_json = str(raw_json)

        # Jeton dérivé du CONTENU (pas d'une clé séparée comme write_seq) : jeton et
        # contenu proviennent de la même valeur, donc toujours cohérents. Le mod
        # écrit chaque clé dans une transaction distincte ; se fier à write_seq
        # exposerait à lire un nouveau compteur avec un gamestate encore périmé,
        # et donc à « sauter » un tour.
        token = zlib.crc32(raw_json.encode("utf-8")) if raw_json is not None else None
        return SourceSnapshot(exists=True, change_token=token, raw_json=raw_json)

    def _read_values(self, conn: sqlite3.Connection) -> dict[str, object]:
        cursor = conn.execute(
            "SELECT Name, Value FROM SimpleValues WHERE Name = ?",
            (GAMESTATE_KEY,),
        )
        return {name: value for name, value in cursor.fetchall()}


def build_source(kind: str, *, db_path: Path, file_path: Path) -> GameStateSource:
    """Fabrique la source selon la configuration ('sqlite' par défaut sur macOS)."""
    if kind == "file":
        return FileGameStateSource(file_path)
    return SqliteModUserDataSource(db_path)
