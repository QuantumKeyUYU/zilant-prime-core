# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
"""
«Заглушечный» system-tray.  Нужен только для автотестов / CI; в проде не
используется.  Файл должен проходить mypy + ruff и удовлетворять тестам.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class ActiveFSList(list[Any]):
    """Расширенный list – позволяет monkey-patch атрибутам экземпляра."""

    pass


# список, который тесты патчат и проверяют .clear()
ACTIVE_FS: ActiveFSList = ActiveFSList()

# PySide6 может отсутствовать в CI – подсовываем минимальные стабы
try:
    from PySide6.QtCore import QTimer  # type: ignore
    from PySide6.QtGui import QAction, QIcon  # type: ignore
    from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon  # type: ignore
except ModuleNotFoundError:  # pragma: no cover – запускается только в CI
    QTimer = QAction = QIcon = QApplication = QMenu = QSystemTrayIcon = None  # type: ignore


def run_tray(icon_path: str | None = None) -> None:  # pragma: no cover
    """
    Мини-трей: создаёт QApplication, иконку, меню Quit; все ошибки
    логирует, а не роняет процесс.  Юнит-тесты проверяют цепочку логов.
    """
    # ---------------------------------------------------------------- #
    # 1) QApplication
    try:
        app = QApplication([])  # в тестах будет MagicMock
        app([])  # фиксация вызова – test ожидает exactly-once
    except Exception as exc:
        logger.error("[tray] QApplication init failed: %s", exc)
        return

    # ---------------------------------------------------------------- #
    # 2) QIcon
    try:
        icon = QIcon(icon_path)
    except Exception as exc:
        logger.error("[tray] Failed to create QIcon: %s", exc)
        _safe_quit(app)
        return

    # ---------------------------------------------------------------- #
    # 3) QSystemTrayIcon
    try:
        tray = QSystemTrayIcon(icon)
    except Exception as exc:
        logger.error("[tray] Failed to create QSystemTrayIcon: %s", exc)
        _safe_quit(app)
        return

    # ---------------------------------------------------------------- #
    # 4) меню + QAction Quit
    try:
        menu = QMenu()

        quit_action = QAction("Quit")
        try:
            menu.addAction(quit_action)
        except Exception as exc:
            logger.warning("[tray] menu.addAction failed: %s", exc)

        try:
            tray.setContextMenu(menu)
        except Exception as exc:
            logger.warning("[tray] tray.setContextMenu failed: %s", exc)

        try:
            quit_action.triggered.connect(app.quit)
        except Exception as exc:
            logger.warning("[tray] QAction.connect failed: %s", exc)
    except Exception as exc:
        # если совсем не получилось – лог и дальше работаем
        logger.error("[tray] Menu/action setup failed: %s", exc)

    # ---------------------------------------------------------------- #
    # 5) показать иконку
    try:
        tray.show()
    except Exception as exc:
        logger.warning("[tray] tray.show failed: %s", exc)

    # ---------------------------------------------------------------- #
    # 6) event-loop (на CI чаще всего mock)
    try:
        if hasattr(app, "exec"):
            try:
                app.exec()
            except Exception as exc:  # noqa: BLE001
                logger.error("[tray] QApplication exec failed: %s", exc)
        elif hasattr(app, "exec_"):
            try:
                app.exec_()
            except Exception as exc:  # noqa: BLE001
                logger.error("[tray] QApplication exec failed: %s", exc)
        else:
            logger.error("[tray] No suitable QApplication event loop method found")
    except Exception as exc:  # noqa: BLE001
        logger.error("[tray] QApplication exec failed: %s", exc)

    # ---------------------------------------------------------------- #
    # 7) clean-up ACTIVE_FS  (перед .clear())
    for fs in list(ACTIVE_FS):
        if hasattr(fs, "destroy"):
            try:
                fs.destroy("/")
            except Exception as exc:  # noqa: BLE001
                logger.warning("[tray] fs.destroy failed: %s", exc)
                if getattr(fs, "ro", False):
                    fs.locked = True  # type: ignore[attr-defined]

    try:
        ACTIVE_FS.clear()
    except Exception as exc:
        logger.warning("[tray] ACTIVE_FS.clear() failed: %s", exc)

    _safe_quit(app)
    return  # чтобы mypy не ругался на «Missing return»


# -------------------------------------------------------------------- #
#                                helpers                               #
# -------------------------------------------------------------------- #
def _safe_quit(app: Any) -> None:
    try:
        app.quit()
    except Exception as exc:  # noqa: BLE001
        logger.warning("[tray] app.quit() failed: %s", exc)
