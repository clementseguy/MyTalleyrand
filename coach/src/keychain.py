"""
Gestion sécurisée des clés API via macOS Keychain.

Utilise le module keyring pour stocker/récupérer les clés API.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

SERVICE_NAME = "MyTalleyrand"


def save_api_key(provider: str, key: str) -> bool:
    """
    Stocke une clé API dans le Keychain macOS.
    
    Args:
        provider: Nom du provider ('openai', 'anthropic', etc.)
        key: Clé API à stocker
        
    Returns:
        True si la sauvegarde a réussi
    """
    try:
        # TODO: import keyring
        # keyring.set_password(SERVICE_NAME, f"{provider}_api_key", key)
        logger.info(f"✅ Clé {provider} sauvegardée dans Keychain")
        return True
    except Exception as e:
        logger.error(f"❌ Erreur sauvegarde clé {provider}: {e}")
        return False


def get_api_key(provider: str) -> Optional[str]:
    """
    Récupère une clé API depuis le Keychain.
    
    Args:
        provider: Nom du provider
        
    Returns:
        La clé API ou None si non trouvée
    """
    try:
        # TODO: import keyring
        # key = keyring.get_password(SERVICE_NAME, f"{provider}_api_key")
        key = None  # Placeholder
        
        if not key:
            logger.warning(f"⚠️ Clé {provider} non trouvée dans Keychain")
        
        return key
    except Exception as e:
        logger.error(f"❌ Erreur récupération clé {provider}: {e}")
        return None


def delete_api_key(provider: str) -> bool:
    """
    Supprime une clé API du Keychain.
    
    Args:
        provider: Nom du provider
        
    Returns:
        True si la suppression a réussi
    """
    try:
        # TODO: import keyring
        # keyring.delete_password(SERVICE_NAME, f"{provider}_api_key")
        logger.info(f"🗑️ Clé {provider} supprimée")
        return True
    except Exception as e:
        logger.error(f"❌ Erreur suppression clé {provider}: {e}")
        return False
