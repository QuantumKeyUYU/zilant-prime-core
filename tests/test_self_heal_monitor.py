# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

from zilant_prime_core.self_heal.monitor import _Handler


def test_handler_on_modified_calls_all(monkeypatch, tmp_path):
    called = {}
    monkeypatch.setattr(
        "zilant_prime_core.self_heal.monitor.rotate_key",
        lambda key: called.setdefault("rotate_key", True),
    )
    monkeypatch.setattr(
        "zilant_prime_core.self_heal.monitor.record_event",
        lambda event: called.setdefault("record_event", True),
    )
    monkeypatch.setattr(
        "zilant_prime_core.self_heal.monitor.prove_intact",
        lambda digest: called.setdefault("prove_intact", True),
    )
    monkeypatch.setattr(
        "zilant_prime_core.self_heal.monitor.maybe_self_destruct",
        lambda path: called.setdefault("maybe_self_destruct", True),
    )
    handler = _Handler(tmp_path / "file.txt")

    class DummyEvent:
        src_path = str(tmp_path / "file.txt")

    handler.on_modified(DummyEvent())
    for k in ["rotate_key", "record_event", "prove_intact", "maybe_self_destruct"]:
        assert called[k] is True
