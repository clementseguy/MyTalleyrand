"""Vérifications de premier lancement et guidage macOS."""

from __future__ import annotations

import platform
from dataclasses import dataclass
from pathlib import Path

from src.config import AppConfig
from src.overlay import is_macos_accessibility_trusted


@dataclass(frozen=True)
class OnboardingCheck:
    """Résultat d'une vérification de premier lancement."""

    name: str
    ok: bool
    message: str
    suggestion: str


def _can_write_directory(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".mytalleyrand_write_test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
    except OSError:
        return False
    return True


def build_onboarding_checks(config: AppConfig) -> list[OnboardingCheck]:
    """Construit les vérifications utiles avant une première partie."""
    checks = [
        OnboardingCheck(
            name="Dossier Civ5",
            ok=config.civ5_dir.exists(),
            message=f"Dossier Civ5 configuré: {config.civ5_dir}",
            suggestion="Lancez Civilization V une première fois ou ajustez TALLEYRAND_CIV5_DIR.",
        ),
        OnboardingCheck(
            name="Dossier export",
            ok=_can_write_directory(config.export_dir),
            message=f"Dossier export accessible en écriture: {config.export_dir}",
            suggestion="Vérifiez l'installation du mod et les permissions du dossier MODS/MyTalleyrand/export.",
        ),
        OnboardingCheck(
            name="Clé API OpenAI",
            ok=bool(config.llm_api_key),
            message="Clé API OpenAI configurée pour le provider distant.",
            suggestion="Optionnel: enregistrez une clé avec `python3 -m src.keychain set openai` ou utilisez le fallback local.",
        ),
    ]
    if platform.system() == "Darwin":
        checks.append(
            OnboardingCheck(
                name="Accessibilité macOS",
                ok=is_macos_accessibility_trusted(),
                message="Permission Accessibilité macOS accordée pour un overlay fiable.",
                suggestion="Réglages Système → Confidentialité et sécurité → Accessibilité → ajouter Terminal ou start_coach.command.",
            )
        )
    return checks


def format_onboarding_report(checks: list[OnboardingCheck]) -> str:
    """Formate un rapport lisible en logs/CLI."""
    lines = ["Onboarding MyTalleyrand — vérifications de premier lancement"]
    for check in checks:
        marker = "✅" if check.ok else "⚠️"
        lines.append(f"{marker} {check.name}: {check.message}")
        if not check.ok:
            lines.append(f"   Action: {check.suggestion}")
    return "\n".join(lines)


def onboarding_marker_path(config: AppConfig) -> Path:
    """Retourne le marqueur indiquant que l'onboarding automatique a déjà été affiché."""
    return config.export_dir / ".onboarding_done"


def should_run_first_launch_onboarding(config: AppConfig) -> bool:
    """Indique si l'onboarding automatique doit être montré."""
    return not onboarding_marker_path(config).exists()


def mark_onboarding_done(config: AppConfig) -> None:
    """Persiste le fait que l'onboarding automatique a été présenté."""
    marker = onboarding_marker_path(config)
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text("done\n", encoding="utf-8")
