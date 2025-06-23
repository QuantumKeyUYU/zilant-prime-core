from __future__ import annotations

from pathlib import Path

try:
    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import QApplication, QMenu, QAction, QSystemTrayIcon
except Exception:  # pragma: no cover - optional GUI
    QApplication = None  # type: ignore


ASSETS = Path(__file__).resolve().parent.parent / "docs" / "assets"


def run_tray() -> None:
    if QApplication is None:
        raise RuntimeError("PySide6 is not installed")
    app = QApplication([])
    icon_path = ASSETS / "logo.svg"
    tray = QSystemTrayIcon(QIcon(str(icon_path)))
    menu = QMenu()
    quit_act = QAction("Quit")
    quit_act.triggered.connect(app.quit)
    menu.addAction(quit_act)
    tray.setContextMenu(menu)
    tray.show()
    app.exec()
