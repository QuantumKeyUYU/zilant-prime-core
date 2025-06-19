# tests/test_key_lifecycle.py

import pytest
from hashlib import sha256

import shamir
from src.key_lifecycle import AuditLog, KeyLifecycle, recover_secret, shard_secret


def test_empty_log(tmp_path):
    f = tmp_path / "empty.log"
    f.write_text("")
    log = AuditLog(path=f)
    assert log._last_digest() == b""
    assert log.verify_log() is True


def test_append_and_verify(tmp_path):
    log_path = tmp_path / "audit.log"
    log = AuditLog(path=log_path)
    assert log.verify_log() is True

    log.append_event("evt1")
    assert "evt1" in log_path.read_text()

    # Испорченная строка
    log_path.write_text("nothex evt\n")
    assert log._last_digest() == b""

    # Корректная запись вручную
    d = sha256(b"" + b"evt").digest().hex()
    good = tmp_path / "good.log"
    good.write_text(f"{d} evt\n")
    assert AuditLog(path=good).verify_log() is True

    # Повреждённый лог
    bad = tmp_path / "bad.log"
    bad.write_text("00 evt\n")
    assert not AuditLog(path=bad).verify_log()


def test_derive_and_rotate():
    master = b"\x01" * 32
    sess = KeyLifecycle.derive_session_key(master, "ctx")
    assert isinstance(sess, bytes) and len(sess) > 0

    rotated = KeyLifecycle.rotate_master_key(master, days=7)
    assert isinstance(rotated, bytes) and rotated != sess


def test_shard_and_recover_success():
    secret = (42).to_bytes(2, "big")
    shards = shard_secret(secret, n=3, t=2)
    assert len(shards) == 3

    rec = recover_secret(shards[:2])
    # Сравниваем как числа, чтобы не портить ведущие нули
    assert int.from_bytes(rec, "big") == int.from_bytes(secret, "big")


@pytest.mark.parametrize("n,t", [(3, 0), (3, 4)])
def test_shard_invalid(n, t):
    with pytest.raises(ValueError):
        shard_secret(b"\x00", n=n, t=t)


def test_shard_too_large():
    big = shamir._PRIME.to_bytes(16, "big")
    with pytest.raises(ValueError):
        shard_secret(big, n=1, t=1)


def test_recover_empty_and_invalid():
    assert recover_secret([]) == b""
    with pytest.raises(ValueError):
        recover_secret([b"short"])
