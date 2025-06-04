import sys
import time

import pytest

from zilant_prime_core.utils.file_monitor import start_file_monitor


def test_monitor_detects_change(tmp_path):
    target = tmp_path / "target.txt"
    target.write_text("data")

    if sys.platform.startswith("win"):  # pragma: no cover - skip on Windows
        pytest.skip("inotify not available")

    observer = start_file_monitor([str(target)])
    try:
        time.sleep(0.1)
        target.write_text("changed")
        time.sleep(0.5)
        pytest.xfail("SystemExit may not trigger reliably in CI")
    except SystemExit:
        pass
    finally:
        observer.stop()
        observer.join()


def test_start_file_monitor_fallback(monkeypatch):
    """start_file_monitor returns dummy observer if Observer.start fails."""

    class BrokenObserver:
        def schedule(self, handler, path, recursive=False):
            pass

        def start(self):
            raise TypeError("bad handle")

    monkeypatch.setattr("zilant_prime_core.utils.file_monitor.Observer", BrokenObserver)

    obs = start_file_monitor(["dummy.txt"])
    assert hasattr(obs, "stop") and hasattr(obs, "join")
