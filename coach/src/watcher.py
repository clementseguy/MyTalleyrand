"""
Surveillance du fichier gamestate.json exporté par le mod.

Utilise watchdog pour détecter les modifications et déclencher
l'analyse par le coach.
"""

import logging
from pathlib import Path
from typing import Callable

logger = logging.getLogger(__name__)


class GameStateWatcher:
    """
    Surveille le fichier gamestate.json et notifie lors des modifications.
    
    Attributes:
        export_dir: Répertoire contenant gamestate.json
        callback: Fonction appelée lors d'une mise à jour
    """
    
    def __init__(self, export_dir: Path, callback: Callable[[Path], None]):
        """
        Initialise le watcher.
        
        Args:
            export_dir: Chemin vers le dossier d'export du mod
            callback: Fonction à appeler lors d'une modification
        """
        self.export_dir = export_dir
        self.callback = callback
        self.observer = None
        
        logger.info(f"👁️  GameStateWatcher initialisé sur {export_dir}")
    
    def start(self):
        """Démarre la surveillance."""
        # TODO: Implémenter avec watchdog.observers.Observer
        logger.info("▶️  Surveillance démarrée")
    
    def stop(self):
        """Arrête la surveillance."""
        # TODO: Arrêter l'observer
        logger.info("⏹️  Surveillance arrêtée")
