import pytest

pytest.importorskip("psutil")

from zilant_prime_core.utils.screen_guard import ScreenGuard, SecurityError


def test_screen_guard_detects_process(monkeypatch):
    class DummyProc:
        def __init__(self, name: str) -> None:
            self.info = {"name": name}

    monkeypatch.setattr("psutil.process_iter", lambda attrs=None: [DummyProc("obs.exe")])
    guard = ScreenGuard()
    with pytest.raises(SecurityError):
        guard.assert_secure()
