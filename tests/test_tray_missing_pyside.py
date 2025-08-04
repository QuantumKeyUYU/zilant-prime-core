# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

import importlib
import logging
import pytest
import sys
from unittest.mock import MagicMock

pytestmark = pytest.mark.skipif(
    "PySide6.QtCore" in sys.modules,
    reason="Тесты на заглушках должны запускаться только без PySide6",
)


@pytest.fixture(autouse=True)
def _reload_tray_module():
    import src.zilant_prime_core.tray as tray_module

    importlib.reload(tray_module)
    tray_module.ACTIVE_FS.clear()
    return tray_module


def test_run_tray_qapplication_failure(monkeypatch, caplog, _reload_tray_module):
    tray_module = _reload_tray_module
    mock_qapp_class = MagicMock(side_effect=Exception("QApplication init failed"))
    monkeypatch.setattr(tray_module, "QApplication", mock_qapp_class)
    with caplog.at_level(logging.ERROR):
        tray_module.run_tray("icon.png")
    assert "[tray] QApplication init failed: QApplication init failed" in caplog.text
    mock_qapp_class.assert_called_once()
    assert not tray_module.ACTIVE_FS


def test_run_tray_icon_failure(monkeypatch, caplog, _reload_tray_module):
    tray_module = _reload_tray_module
    app = MagicMock()
    monkeypatch.setattr(tray_module, "QApplication", MagicMock(return_value=app))
    monkeypatch.setattr(tray_module, "QIcon", MagicMock(side_effect=Exception("icon error")))
    with caplog.at_level(logging.ERROR):
        tray_module.run_tray("icon.png")
    assert "[tray] Failed to create QIcon: icon error" in caplog.text
    app.assert_called_once_with([])
    assert not tray_module.ACTIVE_FS


def test_run_tray_systemtrayicon_failure(monkeypatch, caplog, _reload_tray_module):
    tray_module = _reload_tray_module
    app = MagicMock()
    monkeypatch.setattr(tray_module, "QApplication", MagicMock(return_value=app))
    monkeypatch.setattr(tray_module, "QIcon", MagicMock())
    monkeypatch.setattr(tray_module, "QSystemTrayIcon", MagicMock(side_effect=Exception("tray error")))
    with caplog.at_level(logging.ERROR):
        tray_module.run_tray("icon.png")
    assert "[tray] Failed to create QSystemTrayIcon: tray error" in caplog.text
    app.assert_called_once_with([])
    assert not tray_module.ACTIVE_FS


def test_run_tray_menu_action_setup_failure(monkeypatch, caplog, _reload_tray_module):
    tray_module = _reload_tray_module
    app = MagicMock()
    monkeypatch.setattr(tray_module, "QApplication", MagicMock(return_value=app))
    monkeypatch.setattr(tray_module, "QIcon", MagicMock())
    monkeypatch.setattr(tray_module, "QSystemTrayIcon", MagicMock(return_value=MagicMock()))
    monkeypatch.setattr(tray_module, "QMenu", MagicMock(side_effect=Exception("menu setup error")))
    monkeypatch.setattr(tray_module, "QAction", MagicMock(return_value=MagicMock(triggered=MagicMock())))
    with caplog.at_level(logging.ERROR):
        tray_module.run_tray("icon.png")
    assert "[tray] Menu/action setup failed: menu setup error" in caplog.text
    app.assert_called_once_with([])
    assert not tray_module.ACTIVE_FS


def test_run_tray_no_suitable_exec_method(monkeypatch, caplog, _reload_tray_module):
    tray_module = _reload_tray_module
    mock_app_instance_without_exec = MagicMock()
    if hasattr(mock_app_instance_without_exec, "exec"):
        del mock_app_instance_without_exec.exec
    if hasattr(mock_app_instance_without_exec, "exec_"):
        del mock_app_instance_without_exec.exec_
    monkeypatch.setattr(
        tray_module,
        "QApplication",
        MagicMock(return_value=mock_app_instance_without_exec),
    )
    mock_quit_action_instance = MagicMock()
    mock_quit_action_instance.triggered.connect = MagicMock()
    monkeypatch.setattr(tray_module, "QAction", MagicMock(return_value=mock_quit_action_instance))
    monkeypatch.setattr(tray_module, "QSystemTrayIcon", MagicMock())
    monkeypatch.setattr(tray_module, "QMenu", MagicMock())
    monkeypatch.setattr(tray_module, "QIcon", MagicMock())
    with caplog.at_level(logging.ERROR):
        tray_module.run_tray("icon.png")
    assert "[tray] No suitable QApplication event loop method found" in caplog.text
    assert not hasattr(mock_app_instance_without_exec, "exec")
    assert not hasattr(mock_app_instance_without_exec, "exec_")
    assert not tray_module.ACTIVE_FS


def test_run_tray_exec_loop_failure(monkeypatch, caplog, _reload_tray_module):
    tray_module = _reload_tray_module
    mock_app_instance_with_failing_exec = MagicMock()
    mock_app_instance_with_failing_exec.exec.side_effect = Exception("Exec loop failed")
    monkeypatch.setattr(
        tray_module,
        "QApplication",
        MagicMock(return_value=mock_app_instance_with_failing_exec),
    )
    mock_quit_action_instance = MagicMock()
    mock_quit_action_instance.triggered.connect = MagicMock()
    monkeypatch.setattr(tray_module, "QAction", MagicMock(return_value=mock_quit_action_instance))
    monkeypatch.setattr(tray_module, "QSystemTrayIcon", MagicMock())
    monkeypatch.setattr(tray_module, "QMenu", MagicMock())
    monkeypatch.setattr(tray_module, "QIcon", MagicMock())
    with caplog.at_level(logging.ERROR):
        tray_module.run_tray("icon.png")
    assert "[tray] QApplication exec failed: Exec loop failed" in caplog.text
    mock_app_instance_with_failing_exec.exec.assert_called_once()
    assert not tray_module.ACTIVE_FS


def test_run_tray_fs_destroy_failure(monkeypatch, caplog, _reload_tray_module):
    tray_module = _reload_tray_module
    mock_app_instance = MagicMock()
    mock_app_instance.exec.return_value = 0
    monkeypatch.setattr(tray_module, "QApplication", MagicMock(return_value=mock_app_instance))
    mock_quit_action_instance = MagicMock()
    mock_quit_action_instance.triggered.connect = MagicMock()
    monkeypatch.setattr(tray_module, "QAction", MagicMock(return_value=mock_quit_action_instance))
    monkeypatch.setattr(tray_module, "QSystemTrayIcon", MagicMock())
    monkeypatch.setattr(tray_module, "QMenu", MagicMock())
    monkeypatch.setattr(tray_module, "QIcon", MagicMock())
    fs_failing = MagicMock()
    fs_failing.destroy.side_effect = Exception("FS destroy failed")
    fs_failing.locked = False
    fs_failing.ro = True
    tray_module.ACTIVE_FS.append(fs_failing)
    with caplog.at_level(logging.WARNING):
        tray_module.run_tray("icon.png")
    fs_failing.destroy.assert_called_once_with("/")
    assert "[tray] fs.destroy failed: FS destroy failed" in caplog.text
    assert fs_failing.locked is True
    mock_app_instance.exec.assert_called_once()
    assert not tray_module.ACTIVE_FS


def test_run_tray_active_fs_clear_failure(monkeypatch, caplog, _reload_tray_module):
    tray_module = _reload_tray_module
    app = MagicMock()
    monkeypatch.setattr(tray_module, "QApplication", MagicMock(return_value=app))
    monkeypatch.setattr(tray_module, "QIcon", MagicMock())
    monkeypatch.setattr(tray_module, "QSystemTrayIcon", MagicMock(return_value=MagicMock()))
    monkeypatch.setattr(tray_module, "QMenu", MagicMock(return_value=MagicMock()))
    monkeypatch.setattr(tray_module, "QAction", MagicMock(return_value=MagicMock(triggered=MagicMock())))
    mock_fs_no_destroy = MagicMock(spec=object)
    tray_module.ACTIVE_FS.append(mock_fs_no_destroy)
    monkeypatch.setattr(
        tray_module.ACTIVE_FS,
        "clear",
        MagicMock(side_effect=Exception("ACTIVE_FS clear failed")),
    )
    with caplog.at_level(logging.WARNING):
        tray_module.run_tray("icon.png")
    assert "[tray] ACTIVE_FS.clear() failed: ACTIVE_FS clear failed" in caplog.text
    app.exec.assert_called_once()
    assert len(tray_module.ACTIVE_FS) > 0


def test_run_tray_app_quit_failure(monkeypatch, caplog, _reload_tray_module):
    tray_module = _reload_tray_module
    app = MagicMock()
    app.quit.side_effect = Exception("app quit failed")
    monkeypatch.setattr(tray_module, "QApplication", MagicMock(return_value=app))
    monkeypatch.setattr(tray_module, "QIcon", MagicMock())
    monkeypatch.setattr(tray_module, "QSystemTrayIcon", MagicMock(return_value=MagicMock()))
    monkeypatch.setattr(tray_module, "QMenu", MagicMock(return_value=MagicMock()))
    monkeypatch.setattr(tray_module, "QAction", MagicMock(return_value=MagicMock(triggered=MagicMock())))
    with caplog.at_level(logging.WARNING):
        tray_module.run_tray("icon.png")
    assert "[tray] app.quit() failed: app quit failed" in caplog.text
    app.exec.assert_called_once()
    assert not tray_module.ACTIVE_FS
