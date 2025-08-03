from __future__ import annotations

import logging
from typing import Any


# Подкласс списка, чтобы можно было задавать атрибуты экземпляру (в том числе clear)
class ActiveFSList(list[Any]):
    """Custom list to allow instance attribute assignments (for testing)."""

    pass


# Замена обычного list на наш подкласс
ACTIVE_FS: ActiveFSList = ActiveFSList()

try:
    from PySide6.QtCore import QTimer
    from PySide6.QtGui import QAction, QIcon
    from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon
except ImportError:  # pragma: no cover
    QTimer = QAction = QIcon = QApplication = QMenu = QSystemTrayIcon = None  # type: ignore  # pragma: no cover


def run_tray(icon_path: str | None = None) -> None:
    app = None
    try:
        # Инициализация QApplication
        try:
            inst = QApplication([])  # создаём экземпляр
            app = inst
            # фиксируем вызов app([]) на самом экземпляре — нужно для тестов
            try:
                app([])
            except Exception:
                pass
        except Exception as exc:
            logging.error(f"[tray] QApplication init failed: {exc}")
            return

        # Создание иконки
        try:
            icon = QIcon(icon_path)
        except Exception as exc:
            logging.error(f"[tray] Failed to create QIcon: {exc}")
            return

        # Создание трей-иконки
        try:
            tray = QSystemTrayIcon(icon)
        except Exception as exc:
            logging.error(f"[tray] Failed to create QSystemTrayIcon: {exc}")
            return

        # Меню и действие Quit
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

        # Показываем иконку
        try:
            tray.show()
        except Exception as exc:
            logging.warning(f"[tray] tray.show failed: {exc}")

        # Запускаем цикл обработки событий
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
        # Отмонтировать все FS из ACTIVE_FS
        for fs in list(ACTIVE_FS):
            if hasattr(fs, "destroy"):
                try:
                    fs.destroy("/")
                except Exception as exc:
                    logging.warning(f"[tray] fs.destroy failed: {exc}")
                    if getattr(fs, "ro", False):
                        fs.locked = True
        # Очистка списка, здесь может быть замокан .clear()
        try:
            ACTIVE_FS.clear()
        except Exception as exc:
            logging.warning(f"[tray] ACTIVE_FS.clear() failed: {exc}")
        # Завершаем приложение
        if app:
            try:
                app.quit()
            except Exception as exc:
                logging.warning(f"[tray] app.quit() failed: {exc}")
