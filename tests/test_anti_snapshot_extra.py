import json
import os
from pathlib import Path

from zilant_prime_core.utils.anti_snapshot import detect_snapshot


def test_detect_snapshot_creates_file(tmp_path):
    lock = tmp_path / "lock.json"
    assert detect_snapshot(lock) is False
    assert lock.exists()


def test_detect_snapshot_old_timestamp(tmp_path, monkeypatch):
    lock = tmp_path / "lock.json"
    lock.write_text(json.dumps({"pid": os.getpid(), "ts": 0}))
    assert detect_snapshot(lock, max_age=1.0)


def test_detect_snapshot_dead_pid(tmp_path):
    lock = tmp_path / "lock.json"
    lock.write_text(json.dumps({"pid": 999999, "ts": 0}))
    assert detect_snapshot(lock)


def test_detect_snapshot_invalid_json(tmp_path):
    lock = tmp_path / "lock.json"
    lock.write_text("not json")
    assert detect_snapshot(lock)


def test_detect_snapshot_write_error(tmp_path, monkeypatch):
    lock = tmp_path / "lock.json"

    def fail_write(*args, **kwargs):
        raise OSError("boom")

    monkeypatch.setattr(
        Path,
        "write_text",
        lambda self, data: fail_write() if self == lock else Path.write_text(self, data),
    )
    assert detect_snapshot(lock) is False
