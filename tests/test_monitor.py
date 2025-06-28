# tests/test_monitor.py
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

import pytest

import zilant_prime_core.self_heal.monitor as monitor


def test_monitor_container_importerror(monkeypatch, tmp_path):
    """
    Если Observer=None (имитируем отсутствие watchdog) —
    monitor_container должен сразу бросить ImportError.
    """
    monkeypatch.setattr(monitor, "Observer", None)
    with pytest.raises(ImportError) as exc:
        monitor.monitor_container(str(tmp_path / "file.txt"))
    assert "watchdog is required for monitor_container" in str(exc.value)


def test_handler_on_modified(monkeypatch, tmp_path):
    """
    Проверяем, что при модификации файла вызываются все шаги:
    rotate_key, record_event, prove_intact, maybe_self_destruct.
    """
    called = {}

    monkeypatch.setattr(monitor, "rotate_key", lambda key: called.setdefault("rotate_key", True))
    monkeypatch.setattr(monitor, "record_event", lambda ev: called.setdefault("record_event", True))
    monkeypatch.setattr(monitor, "prove_intact", lambda dg: called.setdefault("prove_intact", True))
    monkeypatch.setattr(monitor, "maybe_self_destruct", lambda p: called.setdefault("maybe_self_destruct", True))

    handler = monitor._Handler(tmp_path / "file.txt")

    class DummyEvent:
        src_path = str(tmp_path / "file.txt")

    handler.on_modified(DummyEvent())

    for step in ("rotate_key", "record_event", "prove_intact", "maybe_self_destruct"):
        assert called.get(step), f"{step} was not called"


def test_handler_on_modified_other_path(tmp_path):
    """
    Если путь не совпал — on_modified должна отработать тихо, без ошибок.
    """
    handler = monitor._Handler(tmp_path / "file.txt")

    class DummyEvent:
        src_path = str(tmp_path / "other.txt")

    # Просто проверяем, что не падает
    handler.on_modified(DummyEvent())
