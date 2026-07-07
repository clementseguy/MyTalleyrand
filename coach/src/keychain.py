"""Gestion sécurisée des clés API via macOS Keychain via keyring."""

from __future__ import annotations

import importlib
import importlib.util
import logging
from types import ModuleType

logger = logging.getLogger(__name__)

SERVICE_NAME = "MyTalleyrand"


def _account_name(provider: str) -> str:
    return provider.strip().lower()


def _load_keyring() -> ModuleType | None:
    """Charge keyring si la dépendance optionnelle est installée."""
    if importlib.util.find_spec("keyring") is None:
        logger.warning("Package keyring indisponible — Keychain désactivé")
        return None
    return importlib.import_module("keyring")


def save_api_key(provider: str, key: str) -> bool:
    """Stocke une clé API dans le Keychain macOS via keyring."""
    keyring = _load_keyring()
    if keyring is None:
        return False

    account = _account_name(provider)
    try:
        keyring.set_password(SERVICE_NAME, account, key)
    except Exception as exc:
        logger.warning("Échec sauvegarde Keychain pour %s: %s", account, exc)
        return False

    logger.info("Clé API %s sauvegardée dans le Keychain", account)
    return True


def get_api_key(provider: str) -> str | None:
    """Récupère une clé API depuis le Keychain macOS via keyring."""
    keyring = _load_keyring()
    if keyring is None:
        return None

    account = _account_name(provider)
    try:
        key = keyring.get_password(SERVICE_NAME, account)
    except Exception as exc:
        logger.warning("Échec lecture Keychain pour %s: %s", account, exc)
        return None

    if key:
        logger.info("Clé API %s récupérée depuis le Keychain", account)
    return key


def delete_api_key(provider: str) -> bool:
    """Supprime une clé API du Keychain macOS via keyring."""
    keyring = _load_keyring()
    if keyring is None:
        return False

    account = _account_name(provider)
    try:
        keyring.delete_password(SERVICE_NAME, account)
    except Exception as exc:
        logger.warning("Échec suppression Keychain pour %s: %s", account, exc)
        return False

    logger.info("Clé API %s supprimée du Keychain", account)
    return True
