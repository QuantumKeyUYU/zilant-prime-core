# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

import importlib
import importlib.util
import logging
import pytest
from unittest.mock import MagicMock

if not importlib.util.find_spec("PySide6.QtWidgets"):
    pytest.skip(
        "PySide6.QtWidgets is not available, skipping tests that require it.",
        allow_module_level=True,
    )

pytestmark = pytest.mark.qt


def reload_tray():
    import src.zilant_prime_core.tray as tray_module

    importlib.reload(tray_module)
    tray_module.ACTIVE_FS.clear()
    return tray_module


def test_run_tray_qapplication_failure(monkeypatch, caplog):
    m = reload_tray()
    qapplication_class_mock = MagicMock(side_effect=Exception("boom init"))
    monkeypatch.setattr(m, "QApplication", qapplication_class_mock)
    with caplog.at_level(logging.ERROR):
        m.run_tray("icon.png")
    assert "[tray] QApplication init failed: boom init" in caplog.text
    assert not m.ACTIVE_FS
    qapplication_class_mock.assert_called_once_with([])


def test_run_tray_icon_failure(monkeypatch, caplog):
    m = reload_tray()
    app_instance_mock = MagicMock()
    qapplication_class_mock = MagicMock(return_value=app_instance_mock)
    monkeypatch.setattr(m, "QApplication", qapplication_class_mock)
    monkeypatch.setattr(m, "QIcon", MagicMock(side_effect=Exception("icon error")))
    with caplog.at_level(logging.ERROR):
        m.run_tray("icon.png")
    assert "[tray] Failed to create QIcon: icon error" in caplog.text
    qapplication_class_mock.assert_called_once_with([])
    assert not m.ACTIVE_FS


def test_run_tray_systemtrayicon_failure(monkeypatch, caplog):
    m = reload_tray()
    app_instance_mock = MagicMock()
    qapplication_class_mock = MagicMock(return_value=app_instance_mock)
    monkeypatch.setattr(m, "QApplication", qapplication_class_mock)
    monkeypatch.setattr(m, "QIcon", MagicMock())
    monkeypatch.setattr(m, "QSystemTrayIcon", MagicMock(side_effect=Exception("tray error")))
    with caplog.at_level(logging.ERROR):
        m.run_tray("icon.png")
    assert "[tray] Failed to create QSystemTrayIcon: tray error" in caplog.text
    qapplication_class_mock.assert_called_once_with([])
    assert not m.ACTIVE_FS


def test_run_tray_menu_action_add_failure(monkeypatch, caplog):
    m = reload_tray()
    app_instance_mock = MagicMock()
    qapplication_class_mock = MagicMock(return_value=app_instance_mock)
    monkeypatch.setattr(m, "QApplication", qapplication_class_mock)
    monkeypatch.setattr(m, "QIcon", MagicMock())
    monkeypatch.setattr(m, "QSystemTrayIcon", MagicMock(return_value=MagicMock()))
    mock_menu = MagicMock()
    mock_menu.addAction.side_effect = Exception("add action error")
    monkeypatch.setattr(m, "QMenu", MagicMock(return_value=mock_menu))
    monkeypatch.setattr(m, "QAction", MagicMock())
    with caplog.at_level(logging.WARNING):
        m.run_tray("icon.png")
    assert "[tray] menu.addAction failed: add action error" in caplog.text
    qapplication_class_mock.assert_called_once_with([])
    assert not m.ACTIVE_FS


def test_run_tray_menu_setcontextmenu_failure(monkeypatch, caplog):
    m = reload_tray()
    app_instance_mock = MagicMock()
    qapplication_class_mock = MagicMock(return_value=app_instance_mock)
    monkeypatch.setattr(m, "QApplication", qapplication_class_mock)
    monkeypatch.setattr(m, "QIcon", MagicMock())
    mock_tray = MagicMock()
    mock_tray.setContextMenu.side_effect = Exception("set context menu error")
    monkeypatch.setattr(m, "QSystemTrayIcon", MagicMock(return_value=mock_tray))
    monkeypatch.setattr(m, "QMenu", MagicMock())
    monkeypatch.setattr(m, "QAction", MagicMock())
    with caplog.at_level(logging.WARNING):
        m.run_tray("icon.png")
    assert "[tray] tray.setContextMenu failed: set context menu error" in caplog.text
    qapplication_class_mock.assert_called_once_with([])
    assert not m.ACTIVE_FS


def test_run_tray_action_connect_failure(monkeypatch, caplog):
    m = reload_tray()
    app_instance_mock = MagicMock()
    qapplication_class_mock = MagicMock(return_value=app_instance_mock)
    monkeypatch.setattr(m, "QApplication", qapplication_class_mock)
    monkeypatch.setattr(m, "QIcon", MagicMock())
    monkeypatch.setattr(m, "QSystemTrayIcon", MagicMock(return_value=MagicMock()))
    monkeypatch.setattr(m, "QMenu", MagicMock())
    mock_action = MagicMock()
    mock_action.triggered.connect.side_effect = Exception("connect error")
    monkeypatch.setattr(m, "QAction", MagicMock(return_value=mock_action))
    with caplog.at_level(logging.WARNING):
        m.run_tray("icon.png")
    assert "[tray] QAction.connect failed: connect error" in caplog.text
    qapplication_class_mock.assert_called_once_with([])
    assert not m.ACTIVE_FS


def test_run_tray_menu_action_setup_failure(monkeypatch, caplog):
    m = reload_tray()
    app_instance_mock = MagicMock()
    qapplication_class_mock = MagicMock(return_value=app_instance_mock)
    monkeypatch.setattr(m, "QApplication", qapplication_class_mock)
    monkeypatch.setattr(m, "QIcon", MagicMock())
    monkeypatch.setattr(m, "QSystemTrayIcon", MagicMock(return_value=MagicMock()))
    monkeypatch.setattr(m, "QMenu", MagicMock(side_effect=Exception("menu setup error")))
    monkeypatch.setattr(m, "QAction", MagicMock(return_value=MagicMock(triggered=MagicMock())))
    with caplog.at_level(logging.ERROR):
        m.run_tray("icon.png")
    assert "[tray] Menu/action setup failed: menu setup error" in caplog.text
    qapplication_class_mock.assert_called_once_with([])
    assert not m.ACTIVE_FS


def test_tray_show_fail(monkeypatch, caplog):
    m = reload_tray()
    app = MagicMock()
    monkeypatch.setattr(m, "QApplication", MagicMock(return_value=app))
    monkeypatch.setattr(m, "QIcon", MagicMock())
    mock_tray = MagicMock()
    mock_tray.show.side_effect = Exception("show fail")
    monkeypatch.setattr(m, "QSystemTrayIcon", MagicMock(return_value=mock_tray))
    monkeypatch.setattr(m, "QMenu", MagicMock())
    monkeypatch.setattr(m, "QAction", MagicMock(return_value=MagicMock(triggered=MagicMock())))
    with caplog.at_level(logging.WARNING):
        m.run_tray("icon.png")
    assert "[tray] tray.show failed: show fail" in caplog.text
    mock_tray.show.assert_called_once()
    app.exec.assert_called_once()
    assert not m.ACTIVE_FS


def test_run_tray_exec_loop_failure(monkeypatch, caplog):
    m = reload_tray()
    app = MagicMock()
    app.exec.side_effect = Exception("exec bomb")
    monkeypatch.setattr(m, "QApplication", MagicMock(return_value=app))
    monkeypatch.setattr(m, "QIcon", MagicMock())
    monkeypatch.setattr(m, "QSystemTrayIcon", MagicMock(return_value=MagicMock()))
    monkeypatch.setattr(m, "QMenu", MagicMock(return_value=MagicMock()))
    monkeypatch.setattr(m, "QAction", MagicMock(return_value=MagicMock(triggered=MagicMock())))
    with caplog.at_level(logging.ERROR):
        m.run_tray("icon.png")
    assert "[tray] QApplication exec failed: exec bomb" in caplog.text
    app.exec.assert_called_once()
    assert not m.ACTIVE_FS


def test_active_fs_and_clear(monkeypatch, caplog):
    m = reload_tray()
    app = MagicMock()
    monkeypatch.setattr(m, "QApplication", MagicMock(return_value=app))
    monkeypatch.setattr(m, "QIcon", MagicMock())
    monkeypatch.setattr(m, "QSystemTrayIcon", MagicMock(return_value=MagicMock()))
    monkeypatch.setattr(m, "QMenu", MagicMock(return_value=MagicMock()))
    monkeypatch.setattr(m, "QAction", MagicMock(return_value=MagicMock(triggered=MagicMock())))

    class FS:
        def __init__(self):
            self.destroy_called = False
            self.locked = False
            self.ro = True

        def destroy(self, p):
            self.destroy_called = True
            raise Exception("fs bomb")

    fs = FS()
    m.ACTIVE_FS.append(fs)
    with caplog.at_level(logging.WARNING):
        m.run_tray("icon.png")
    assert "[tray] fs.destroy failed: fs bomb" in caplog.text
    assert fs.locked
    assert not m.ACTIVE_FS


def test_run_tray_active_fs_clear_failure(monkeypatch, caplog):
    m = reload_tray()
    app = MagicMock()
    monkeypatch.setattr(m, "QApplication", MagicMock(return_value=app))
    monkeypatch.setattr(m, "QIcon", MagicMock())
    monkeypatch.setattr(m, "QSystemTrayIcon", MagicMock(return_value=MagicMock()))
    monkeypatch.setattr(m, "QMenu", MagicMock(return_value=MagicMock()))
    monkeypatch.setattr(m, "QAction", MagicMock(return_value=MagicMock(triggered=MagicMock())))
    mock_active_fs = MagicMock()
    mock_active_fs.clear.side_effect = Exception("ACTIVE_FS clear failed")
    monkeypatch.setattr(m, "ACTIVE_FS", mock_active_fs)
    with caplog.at_level(logging.WARNING):
        m.run_tray("icon.png")
    assert "[tray] ACTIVE_FS.clear() failed: ACTIVE_FS clear failed" in caplog.text
    app.exec.assert_called_once()
    mock_active_fs.clear.assert_called_once()


def test_run_tray_app_quit_failure(monkeypatch, caplog):
    m = reload_tray()
    app = MagicMock()
    app.quit.side_effect = Exception("app quit failed")
    monkeypatch.setattr(m, "QApplication", MagicMock(return_value=app))
    monkeypatch.setattr(m, "QIcon", MagicMock())
    monkeypatch.setattr(m, "QSystemTrayIcon", MagicMock(return_value=MagicMock()))
    monkeypatch.setattr(m, "QMenu", MagicMock(return_value=MagicMock()))
    monkeypatch.setattr(m, "QAction", MagicMock(return_value=MagicMock(triggered=MagicMock())))
    with caplog.at_level(logging.WARNING):
        m.run_tray("icon.png")
    assert "[tray] app.quit() failed: app quit failed" in caplog.text
    app.exec.assert_called_once()
    assert not m.ACTIVE_FS


def test_run_tray_exec_method_is_exec_underscore(monkeypatch, caplog):
    m = reload_tray()
    app_instance_mock = MagicMock()
    if hasattr(app_instance_mock, "exec"):
        del app_instance_mock.exec
    app_instance_mock.exec_ = MagicMock(return_value=0)
    qapplication_class_mock = MagicMock(return_value=app_instance_mock)
    monkeypatch.setattr(m, "QApplication", qapplication_class_mock)
    monkeypatch.setattr(m, "QIcon", MagicMock())
    monkeypatch.setattr(m, "QSystemTrayIcon", MagicMock(return_value=MagicMock()))
    monkeypatch.setattr(m, "QMenu", MagicMock(return_value=MagicMock()))
    monkeypatch.setattr(m, "QAction", MagicMock(return_value=MagicMock(triggered=MagicMock())))
    with caplog.at_level(logging.INFO):
        m.run_tray("icon.png")
    app_instance_mock.exec_.assert_called_once()
    assert not hasattr(app_instance_mock, "exec")
    qapplication_class_mock.assert_called_once_with([])


def test_run_tray_no_exec_methods_at_all(monkeypatch, caplog):
    m = reload_tray()
    app_instance_mock = MagicMock()
    if hasattr(app_instance_mock, "exec"):
        del app_instance_mock.exec
    if hasattr(app_instance_mock, "exec_"):
        del app_instance_mock.exec_
    qapplication_class_mock = MagicMock(return_value=app_instance_mock)
    monkeypatch.setattr(m, "QApplication", qapplication_class_mock)
    monkeypatch.setattr(m, "QIcon", MagicMock())
    monkeypatch.setattr(m, "QSystemTrayIcon", MagicMock(return_value=MagicMock()))
    monkeypatch.setattr(m, "QMenu", MagicMock(return_value=MagicMock()))
    monkeypatch.setattr(m, "QAction", MagicMock(return_value=MagicMock(triggered=MagicMock())))
    with caplog.at_level(logging.ERROR):
        m.run_tray("icon.png")
    assert "[tray] No suitable QApplication event loop method found" in caplog.text
    qapplication_class_mock.assert_called_once_with([])
