"""Gestion sécurisée des clés API via macOS Keychain via keyring."""

from __future__ import annotations

import argparse
import getpass
import importlib
import importlib.util
import logging
import sys
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


def _read_secret(use_stdin: bool, provider: str) -> str:
    if use_stdin:
        return sys.stdin.read().strip()
    return getpass.getpass(f"Clé API {provider}: ").strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gère les clés API MyTalleyrand dans le Keychain macOS")
    subparsers = parser.add_subparsers(dest="command", required=True)

    set_parser = subparsers.add_parser("set", help="enregistre une clé API")
    set_parser.add_argument("provider", help="provider LLM, ex: openai")
    set_parser.add_argument("--stdin", action="store_true", help="lit la clé depuis stdin")

    get_parser = subparsers.add_parser("get", help="vérifie si une clé existe")
    get_parser.add_argument("provider", help="provider LLM, ex: openai")

    delete_parser = subparsers.add_parser("delete", help="supprime une clé API")
    delete_parser.add_argument("provider", help="provider LLM, ex: openai")

    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

    if args.command == "set":
        secret = _read_secret(args.stdin, args.provider)
        if not secret:
            parser.error("clé API vide")
        return 0 if save_api_key(args.provider, secret) else 1
    if args.command == "get":
        key = get_api_key(args.provider)
        print("présente" if key else "absente")
        return 0 if key else 1
    if args.command == "delete":
        return 0 if delete_api_key(args.provider) else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
