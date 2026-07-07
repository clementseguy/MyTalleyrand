"""Overlay MyTalleyrand avec backend texte testable et backend PyQt6 optionnel."""

from __future__ import annotations

import ctypes
import importlib.util
import json
import logging
import platform
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from src.llm_client import LLMAdvice

logger = logging.getLogger(__name__)


@dataclass
class OverlayPosition:
    x: int = 30
    y: int = 30


@dataclass
class OverlaySettings:
    width: int = 420
    height: int = 320
    opacity: float = 0.92


class OverlayBackend(Protocol):
    def move_to(self, position: OverlayPosition) -> None: ...

    def render(self, text: str, visible: bool, minimized: bool) -> None: ...

    def close(self) -> None: ...


class TextOverlayBackend:
    """Backend sans UI réelle, utilisé par les tests et les environnements sans PyQt6."""

    def move_to(self, position: OverlayPosition) -> None:
        logger.debug("Backend texte déplacé en (%s,%s)", position.x, position.y)

    def render(self, text: str, visible: bool, minimized: bool) -> None:
        logger.debug(
            "Backend texte rendu (visible=%s, minimized=%s, chars=%s)",
            visible,
            minimized,
            len(text),
        )

    def close(self) -> None:
        logger.debug("Backend texte fermé")


def is_macos_accessibility_trusted() -> bool:
    """Vérifie la permission Accessibilité macOS requise pour un overlay fiable."""
    if platform.system() != "Darwin":
        return True
    app_services = ctypes.cdll.LoadLibrary("/System/Library/Frameworks/ApplicationServices.framework/ApplicationServices")
    app_services.AXIsProcessTrusted.restype = ctypes.c_bool
    return bool(app_services.AXIsProcessTrusted())


class QtOverlayBackend:
    """Fenêtre PyQt6 transparente, persistante et non bloquante pour Civilization V fenêtré."""

    def __init__(self, position: OverlayPosition, settings: OverlaySettings):
        from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt
        from PyQt6.QtGui import QGuiApplication
        from PyQt6.QtWidgets import QApplication, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

        self._qt = Qt
        self._animation_type = QPropertyAnimation
        self._easing_curve = QEasingCurve
        self._app = QApplication.instance() or QApplication([])
        self._window = QWidget()
        self._window.setWindowTitle("MyTalleyrand Coach")
        self._window.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self._window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._window.setWindowOpacity(settings.opacity)
        self._window.resize(settings.width, settings.height)
        # Pas de click-through natif: seuls les clics hors fenêtre compacte restent au jeu.

        self._card = QFrame(self._window)
        self._card.setObjectName("coachCard")
        layout = QVBoxLayout(self._card)
        layout.setContentsMargins(16, 12, 16, 16)
        layout.setSpacing(10)

        header = QHBoxLayout()
        self._title = QLabel("MyTalleyrand")
        self._title.setObjectName("title")
        self._minimize = QPushButton("–")
        self._minimize.setObjectName("chromeButton")
        self._close = QPushButton("×")
        self._close.setObjectName("chromeButton")
        header.addWidget(self._title, 1)
        header.addWidget(self._minimize)
        header.addWidget(self._close)
        layout.addLayout(header)

        self._content = QLabel("En attente d'un conseil…")
        self._content.setObjectName("content")
        self._content.setWordWrap(True)
        self._content.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self._content, 1)
        self._window.setStyleSheet(_QSS)
        self._card.setGeometry(0, 0, settings.width, settings.height)
        self._window.move(*self._clamp_to_available_screen(position.x, position.y))
        self._window.show()
        self._fade_in()
        self._app.processEvents()
        screen_names = [screen.name() for screen in QGuiApplication.screens()]
        logger.info("Écrans détectés pour l'overlay: %s", ", ".join(screen_names) or "aucun")

    @property
    def minimize_button(self):
        return self._minimize

    @property
    def close_button(self):
        return self._close

    def move_to(self, position: OverlayPosition) -> None:
        self._window.move(*self._clamp_to_available_screen(position.x, position.y))
        self._app.processEvents()

    def _clamp_to_available_screen(self, x: int, y: int) -> tuple[int, int]:
        from PyQt6.QtCore import QPoint
        from PyQt6.QtGui import QGuiApplication

        screen = QGuiApplication.screenAt(QPoint(x, y)) or QGuiApplication.primaryScreen()
        if screen is None:
            return max(0, x), max(0, y)

        geometry = screen.availableGeometry()
        max_x = max(geometry.left(), geometry.right() - self._window.width())
        max_y = max(geometry.top(), geometry.bottom() - self._window.height())
        clamped_x = min(max(x, geometry.left()), max_x)
        clamped_y = min(max(y, geometry.top()), max_y)
        return clamped_x, clamped_y

    def render(self, text: str, visible: bool, minimized: bool) -> None:
        self._content.setText(text)
        self._content.setVisible(not minimized)
        if visible:
            self._window.show()
            self._fade_in()
        else:
            self._window.hide()
        self._app.processEvents()

    def close(self) -> None:
        self._window.hide()
        self._app.processEvents()

    def _fade_in(self) -> None:
        animation = self._animation_type(self._window, b"windowOpacity")
        animation.setDuration(160)
        animation.setStartValue(0.0)
        animation.setEndValue(self._window.windowOpacity())
        animation.setEasingCurve(self._easing_curve.Type.OutCubic)
        animation.start()
        self._animation = animation


_QSS = """
#coachCard {
  background: rgba(23, 29, 39, 235);
  border: 1px solid rgba(221, 190, 122, 190);
  border-radius: 16px;
}
#title {
  color: #f5d88f;
  font-family: Inter, Helvetica, Arial, sans-serif;
  font-size: 18px;
  font-weight: 700;
}
#content {
  color: #f7f3e8;
  font-family: Inter, Helvetica, Arial, sans-serif;
  font-size: 14px;
  line-height: 1.35;
}
#chromeButton {
  color: #f7f3e8;
  background: rgba(255, 255, 255, 24);
  border: 1px solid rgba(255, 255, 255, 45);
  border-radius: 10px;
  min-width: 28px;
  min-height: 24px;
}
#chromeButton:hover { background: rgba(245, 216, 143, 52); }
"""


class TalleyrandOverlay:
    """Contrôleur d'overlay: état persistant, rendu de conseils et backend UI."""

    def __init__(
        self,
        state_file: Path,
        settings: OverlaySettings | None = None,
        backend: OverlayBackend | None = None,
        enable_qt: bool = False,
    ):
        self.state_file = state_file
        self.settings = settings or OverlaySettings()
        self.visible = True
        self.minimized = False
        self.position = OverlayPosition()
        self.last_rendered_text = ""
        self._load_state()
        self.backend = backend or self._build_backend(enable_qt=enable_qt)
        self._wire_backend_controls()
        logger.info("🖼️ Overlay initialisé en (%s,%s)", self.position.x, self.position.y)

    def _build_backend(self, enable_qt: bool) -> OverlayBackend:
        if enable_qt and importlib.util.find_spec("PyQt6") is not None:
            if not is_macos_accessibility_trusted():
                logger.warning("Permission Accessibilité macOS absente: l'overlay peut ne pas rester au-dessus de Civ5.")
            return QtOverlayBackend(position=self.position, settings=self.settings)
        if enable_qt:
            logger.warning("PyQt6 indisponible: fallback vers overlay texte testable")
        return TextOverlayBackend()

    def _wire_backend_controls(self) -> None:
        if isinstance(self.backend, QtOverlayBackend):
            self.backend.minimize_button.clicked.connect(self.minimize)
            self.backend.close_button.clicked.connect(self.hide)

    def _load_state(self) -> None:
        if not self.state_file.exists():
            return
        try:
            payload = json.loads(self.state_file.read_text(encoding="utf-8"))
            self.position = OverlayPosition(x=int(payload.get("x", 30)), y=int(payload.get("y", 30)))
            self.visible = bool(payload.get("visible", True))
            self.minimized = bool(payload.get("minimized", False))
        except (json.JSONDecodeError, ValueError, TypeError) as exc:
            logger.warning("État overlay corrompu, réinitialisation (%s)", exc)

    def _save_state(self) -> None:
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "x": self.position.x,
            "y": self.position.y,
            "visible": self.visible,
            "minimized": self.minimized,
        }
        self.state_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def move_to(self, x: int, y: int) -> None:
        self.position = OverlayPosition(x=max(0, x), y=max(0, y))
        self._save_state()
        self.backend.move_to(self.position)

    def toggle_visibility(self) -> bool:
        return self.show() if not self.visible else self.hide()

    def show(self) -> bool:
        self.visible = True
        self._save_state()
        self.backend.render(self.last_rendered_text, self.visible, self.minimized)
        return self.visible

    def hide(self) -> bool:
        self.visible = False
        self._save_state()
        self.backend.render(self.last_rendered_text, self.visible, self.minimized)
        return self.visible

    def minimize(self) -> None:
        self.minimized = True
        self.visible = True
        self._save_state()
        self.backend.render(self.last_rendered_text, self.visible, self.minimized)

    def close(self) -> None:
        self.hide()
        self.backend.close()

    def show_advice(self, advice: LLMAdvice) -> None:
        self.minimized = False
        lines = []
        if advice.source == "local_fallback":
            lines.extend(
                [
                    "Fallback LLM activé: conseil local affiché car le provider distant est indisponible.",
                    "Action suggérée: vérifiez votre réseau ou votre clé API ; nouvel essai automatique au prochain tour analysé.",
                    "",
                ]
            )
        lines.extend(
            [
                f"Objectif (10 tours): {advice.objective_10_turns}",
                "Actions prioritaires:",
            ]
        )
        lines.extend([f"- {action}" for action in advice.priority_actions])
        if advice.risks:
            lines.append("Risques:")
            lines.extend([f"- {risk}" for risk in advice.risks])
        self.last_rendered_text = "\n".join(lines)
        self._save_state()
        self.backend.render(self.last_rendered_text, self.visible, self.minimized)
        logger.info("💬 Overlay mis à jour avec %s actions", len(advice.priority_actions))

    def show_status(self, title: str, message: str, suggestion: str, critical: bool = True) -> None:
        self.last_rendered_text = "\n".join(
            [
                f"{title}: {message}",
                f"Action suggérée: {suggestion}",
            ]
        )
        if critical:
            self.visible = True
            self.minimized = False
            self._save_state()
        self.backend.render(self.last_rendered_text, self.visible, self.minimized)
        logger.warning("⚠️ Overlay statut: %s", title)
