"""Tests du stockage Keychain via l'adaptateur keyring."""

from __future__ import annotations

from src import keychain


class FakeKeyring:
    def __init__(self):
        self.values: dict[tuple[str, str], str] = {}

    def set_password(self, service: str, account: str, key: str) -> None:
        self.values[(service, account)] = key

    def get_password(self, service: str, account: str) -> str | None:
        return self.values.get((service, account))

    def delete_password(self, service: str, account: str) -> None:
        self.values.pop((service, account), None)


def test_keychain_round_trip_with_keyring_adapter(monkeypatch):
    fake_keyring = FakeKeyring()
    monkeypatch.setattr(keychain, "_load_keyring", lambda: fake_keyring)

    assert keychain.save_api_key(" OpenAI ", "sk-test") is True
    assert keychain.get_api_key("openai") == "sk-test"
    assert keychain.delete_api_key("OPENAI") is True
    assert keychain.get_api_key("openai") is None


def test_keychain_returns_safe_defaults_when_keyring_missing(monkeypatch):
    monkeypatch.setattr(keychain, "_load_keyring", lambda: None)

    assert keychain.save_api_key("openai", "sk-test") is False
    assert keychain.get_api_key("openai") is None
    assert keychain.delete_api_key("openai") is False
