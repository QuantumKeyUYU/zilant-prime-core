# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

import types

import pytest

import zilant_prime_core.watchdog as wd


def test_watchdog_start_stop(monkeypatch, tmp_path):
    events = []
    class FakeProcess:
        def __init__(self, target=None, args=()) -> None:
            events.append((target, args))
            self.pid = 1
        def start(self):
            events.append("start")
        def terminate(self):
            events.append("term")
        def join(self):
            events.append("join")
    monkeypatch.setattr(wd, "Process", FakeProcess)
    w = wd.Watchdog("x", 0.1, watch_dir=tmp_path)
    w.start()
    w.stop()
    assert "start" in events and "term" in events


def test_proc_a_and_b(monkeypatch, tmp_path):
    rec = []
    q = types.SimpleNamespace(put=lambda v: rec.append(v))
    monkeypatch.setattr(wd, "_hash_sources", lambda x: "h")
    monkeypatch.setattr(wd, "time", types.SimpleNamespace(monotonic=lambda: 1.0, sleep=lambda n: (_ for _ in ()).throw(SystemExit)))
    with pytest.raises(SystemExit):
        wd._proc_a(tmp_path, "h", 0.01, q)
    assert rec == [1.0]

    q2 = types.SimpleNamespace(get=lambda timeout=None: (_ for _ in ()).throw(FileNotFoundError()))
    monkeypatch.setattr(wd, "os", types.SimpleNamespace(kill=lambda pid, sig: (_ for _ in ()).throw(Exception())))
    monkeypatch.setattr(wd, "time", types.SimpleNamespace(monotonic=lambda: 1.0, sleep=lambda n: (_ for _ in ()).throw(SystemExit)))
    with pytest.raises(SystemExit):
        wd._proc_b(123, q2, 0.01)

