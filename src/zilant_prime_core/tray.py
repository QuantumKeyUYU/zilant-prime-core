from __future__ import annotations

import logging


class _ActiveList(list):
    """List subclass allowing attribute patching during tests."""


ACTIVE_FS: _ActiveList = _ActiveList()

try:
    from PySide6.QtCore import QTimer
    from PySide6.QtGui import QAction, QIcon
    from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon
except ImportError:  # pragma: no cover
    QTimer = QAction = QIcon = QApplication = QMenu = QSystemTrayIcon = None  # type: ignore  # pragma: no cover


def run_tray(icon_path: str | None = None) -> None:
    app = None
    try:
        try:
            app = QApplication([])
        except Exception as exc:
            logging.error(f"[tray] QApplication init failed: {exc}")
            return

        try:
            icon = QIcon(icon_path)
        except Exception as exc:
            logging.error(f"[tray] Failed to create QIcon: {exc}")
            return

        try:
            tray = QSystemTrayIcon(icon)
        except Exception as exc:
            logging.error(f"[tray] Failed to create QSystemTrayIcon: {exc}")
            return

        try:
            menu = QMenu()
            quit_action = QAction("Quit")
            try:
                menu.addAction(quit_action)
            except Exception as exc:
                logging.warning(f"[tray] menu.addAction failed: {exc}")
            try:
                tray.setContextMenu(menu)
            except Exception as exc:
                logging.warning(f"[tray] tray.setContextMenu failed: {exc}")
            try:
                quit_action.triggered.connect(app.quit)
            except Exception as exc:
                logging.warning(f"[tray] QAction.connect failed: {exc}")
        except Exception as exc:
            logging.error(f"[tray] Menu/action setup failed: {exc}")

        try:
            tray.show()
        except Exception as exc:
            logging.warning(f"[tray] tray.show failed: {exc}")

        try:
            if hasattr(app, "exec"):
                app.exec()
            elif hasattr(app, "exec_"):
                app.exec_()
            else:
                logging.error("[tray] No suitable QApplication event loop method found")
        except Exception as exc:
            logging.error(f"[tray] QApplication exec failed: {exc}")

    finally:
        for fs in list(ACTIVE_FS):
            if hasattr(fs, "destroy"):
                try:
                    fs.destroy("/")
                except Exception as exc:
                    logging.warning(f"[tray] fs.destroy failed: {exc}")
                    if getattr(fs, "ro", False):
                        fs.locked = True
        try:
            ACTIVE_FS.clear()
        except Exception as exc:
            logging.warning(f"[tray] ACTIVE_FS.clear() failed: {exc}")
        if app:
            try:
                app.quit()
            except Exception as exc:
                logging.warning(f"[tray] app.quit() failed: {exc}")
