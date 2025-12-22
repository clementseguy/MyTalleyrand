#!/usr/bin/env python3
"""
Point d'entrée principal de l'application Talleyrand Coach.

Lance la surveillance du fichier gamestate.json et l'overlay UI.
"""

import sys
import logging
from pathlib import Path

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path.home() / 'talleyrand.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Point d'entrée principal de l'application."""
    logger.info("🎮 Démarrage de Talleyrand Coach...")
    
    # TODO: Importer et lancer les composants
    # from watcher import GameStateWatcher
    # from overlay import TalleyrandOverlay
    # from coach import CoachEngine
    
    logger.info("✅ Talleyrand Coach initialisé")
    logger.info("En attente de parties Civilization V...")
    
    # Boucle principale (placeholder)
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("⏹️  Arrêt de Talleyrand Coach")


if __name__ == "__main__":
    main()
