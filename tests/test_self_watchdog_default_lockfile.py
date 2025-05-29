# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

# tests/test_self_watchdog_default_lockfile.py


import zilant_prime_core.utils.self_watchdog as wd


class DummyLock:
    def __init__(self, lock_file):
        # запоминаем, каким именем пользовались
        DummyLock.lock_file = lock_file

    def acquire(self):
        pass


class DummyThread:
    def __init__(self, target, args, daemon):
        DummyThread.created = True
        DummyThread.args = args

    def start(self):
        pass


def test_init_self_watchdog_default_lockfile(monkeypatch, tmp_path):
    # создаём тестовый "модуль" на диске
    mod = tmp_path / "mymod.py"
    mod.write_text("data")

    # мокаем FileLock, compute_self_hash и Thread
    monkeypatch.setattr(wd, "FileLock", DummyLock)
    monkeypatch.setattr(wd, "compute_self_hash", lambda fp: "XYZ")
    monkeypatch.setattr(wd.threading, "Thread", DummyThread)

    # вызываем без lock_file
    wd.init_self_watchdog(module_file=str(mod), interval=5)

    # default lock_file должен быть module_file + ".lock"
    expected = str(mod) + ".lock"
    assert DummyLock.lock_file == expected

    # И поток должен быть создан с нашими аргументами
    assert getattr(DummyThread, "created", False)
    mf, h, interv = DummyThread.args
    assert mf == str(mod)
    assert h == "XYZ"
    assert interv == 5
