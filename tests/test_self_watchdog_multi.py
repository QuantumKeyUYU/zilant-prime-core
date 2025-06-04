import pytest

from zilant_prime_core.utils.self_watchdog import init_self_watchdog


def test_cross_watchdog_exits_when_parent_dead(monkeypatch):
    monkeypatch.setenv("ZILANT_NO_SANDBOX", "1")
    monkeypatch.setattr("os.getppid", lambda: 999999)

    def fake_kill(pid, sig):
        raise OSError

    monkeypatch.setattr("os.kill", fake_kill)
    with pytest.raises(SystemExit):
        init_self_watchdog(module_file=__file__, interval=0.01)
