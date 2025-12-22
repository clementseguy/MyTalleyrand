"""
Interface overlay PyQt6 pour afficher les conseils du coach.

Fenêtre transparente positionnée au-dessus de Civilization V.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TalleyrandOverlay:
    """
    Overlay UI affichant les conseils du coach.
    
    Fenêtre PyQt6 transparente avec WindowStaysOnTopHint.
    """
    
    def __init__(self):
        """Initialise l'overlay."""
        # TODO: Créer QWidget avec flags appropriés
        logger.info("🖼️  TalleyrandOverlay initialisé")
    
    def show_advice(self, advice: str):
        """
        Affiche un conseil du coach.
        
        Args:
            advice: Texte du conseil à afficher
        """
        logger.info(f"💬 Affichage conseil: {advice[:50]}...")
    
    def hide(self):
        """Masque l'overlay."""
        logger.info("👁️‍🗨️ Overlay masqué")
    
    def show(self):
        """Affiche l'overlay."""
        logger.info("👁️ Overlay affiché")
