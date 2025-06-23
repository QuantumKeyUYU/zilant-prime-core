from __future__ import annotations

from pathlib import Path

from container import get_metadata
from .zilfs import ACTIVE_FS

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

    def _lock_all() -> None:
        for fs in list(ACTIVE_FS):
            fs.destroy("/")

    def refresh() -> None:
        menu.clear()
        lock_act = QAction("Lock all")
        lock_act.triggered.connect(_lock_all)
        menu.addAction(lock_act)
        for fs in ACTIVE_FS:
            meta = get_metadata(fs.container)
            snaps = len(meta.get("snapshots", {}))
            rate = fs.throughput_mb_s()
            label = f"{fs.container.name} {rate:.1f} MB/s"
            act = QAction(label)
            if fs.ro:
                act.setText("🛑 " + label)
            menu.addAction(act)
            act.setToolTip(f"snapshots: {snaps}")
        menu.addSeparator()
        quit_act = QAction("Quit")
        quit_act.triggered.connect(app.quit)
        menu.addAction(quit_act)
        tray.setContextMenu(menu)

    tray.activated.connect(lambda _: refresh())
    refresh()
    tray.show()
    app.exec()
