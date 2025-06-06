import time

from zilant_prime_core.utils.anti_snapshot import detect_snapshot, read_timestamp, write_timestamp


def test_write_timestamp_uses_now(tmp_path, monkeypatch):
    monkeypatch.setattr("zilant_prime_core.utils.anti_snapshot.TIMESTAMP_FILE", tmp_path / "ts.txt")
    monkeypatch.setattr(time, "time", lambda: 111.0)
    write_timestamp()
    assert abs(read_timestamp() - 111.0) < 1e-6


def test_detect_snapshot_updates_timestamp(tmp_path, monkeypatch):
    monkeypatch.setattr("zilant_prime_core.utils.anti_snapshot.TIMESTAMP_FILE", tmp_path / "ts.txt")
    monkeypatch.setattr(time, "time", lambda: 100.0)
    assert detect_snapshot() is False
    monkeypatch.setattr(time, "time", lambda: 101.0)
    assert detect_snapshot() is False
    assert abs(read_timestamp() - 101.0) < 1e-6
