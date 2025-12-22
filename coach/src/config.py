"""
Configuration de l'application coach.

Gère les paramètres, chemins et clés API.
"""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


# Chemins par défaut macOS (Aspyr)
CIV5_USER_DIR = Path.home() / "Documents/Aspyr/Sid Meier's Civilization 5"
MOD_EXPORT_DIR = CIV5_USER_DIR / "MODS/MyTalleyrand/export"
GAMESTATE_FILE = MOD_EXPORT_DIR / "gamestate.json"

# Configuration LLM
DEFAULT_LLM_PROVIDER = "openai"
DEFAULT_MODEL = "gpt-4o-mini"
MAX_TOKENS = 500
TEMPERATURE = 0.7

# Configuration UI
OVERLAY_WIDTH = 400
OVERLAY_HEIGHT = 600
OVERLAY_OPACITY = 0.9


class Config:
    """Classe de configuration centralisée."""
    
    def __init__(self):
        """Charge la configuration."""
        self.civ5_dir = CIV5_USER_DIR
        self.export_dir = MOD_EXPORT_DIR
        self.gamestate_file = GAMESTATE_FILE
        
        self.llm_provider = DEFAULT_LLM_PROVIDER
        self.llm_model = DEFAULT_MODEL
        self.api_key: Optional[str] = None
        
        logger.info("⚙️  Configuration chargée")
    
    def validate(self) -> bool:
        """
        Valide la configuration.
        
        Returns:
            True si la configuration est valide
        """
        if not self.civ5_dir.exists():
            logger.error(f"❌ Répertoire Civ5 introuvable: {self.civ5_dir}")
            return False
        
        if not self.api_key:
            logger.error("❌ Clé API manquante")
            return False
        
        logger.info("✅ Configuration valide")
        return True
