import os
import time

from zilant_prime_core.utils.self_watchdog import init_self_watchdog


def test_child_monitor_exit(monkeypatch, tmp_path):
    mod = tmp_path / "m.py"
    mod.write_text("x=1")
    lock = str(mod) + ".lock"

    calls = {}

    def fake_exit(code):
        calls["code"] = code
        raise SystemExit

    monkeypatch.setattr(os, "_exit", fake_exit)
    monkeypatch.setattr(os, "kill", lambda *a, **kw: (_ for _ in ()).throw(OSError()))

    init_self_watchdog(module_file=str(mod), lock_file=lock, interval=0.01)
    time.sleep(0.05)
    assert calls.get("code") == 134
