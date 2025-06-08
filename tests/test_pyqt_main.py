import pytest

pytest.importorskip("PyQt5.QtWidgets")

from ui.pyqt.main import MainWindow


def test_mainwindow_creation():
    win = MainWindow()
    assert win.pack_button.text() == "Pack"
    assert win.unpack_button.text() == "Unpack"
    assert win.cancel_button.text() == "Panic"
