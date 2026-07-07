"""
Gestion sécurisée des clés API via macOS Keychain.

Stub : l'intégration réelle via le module keyring est prévue (voir BACKLOG US non planifiée).
Toutes les fonctions lèvent NotImplementedError tant que keyring n'est pas intégré.
"""

import logging

logger = logging.getLogger(__name__)

SERVICE_NAME = "MyTalleyrand"


def save_api_key(provider: str, key: str) -> bool:
    """Stocke une clé API dans le Keychain macOS (non implémenté)."""
    logger.warning("Keychain non implémenté — clé %s non sauvegardée", provider)
    raise NotImplementedError("Intégration keyring non encore active")


def get_api_key(provider: str) -> str | None:
    """Récupère une clé API depuis le Keychain (non implémenté)."""
    logger.warning("Keychain non implémenté — clé %s non disponible", provider)
    return None


def delete_api_key(provider: str) -> bool:
    """Supprime une clé API du Keychain (non implémenté)."""
    logger.warning("Keychain non implémenté — clé %s non supprimée", provider)
    raise NotImplementedError("Intégration keyring non encore active")
