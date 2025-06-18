import hashlib

from key_lifecycle import AuditLog, KeyLifecycle, recover_secret, shard_secret


def test_derive_and_rotate():
    master = b"m" * 32
    ctx = "ctx"
    expected = hashlib.blake2s(ctx.encode(), key=master).digest()
    assert KeyLifecycle.derive_session_key(master, ctx) == expected

    expected_rot = hashlib.blake2s((3).to_bytes(4, "big"), key=master).digest()
    assert KeyLifecycle.rotate_master_key(master, 3) == expected_rot


def test_shard_and_recover():
    secret = b"sec"
    shards = shard_secret(secret, 5, 3)
    assert len(shards) == 5
    assert recover_secret(shards[:3]) == secret


def test_audit_log(tmp_path):
    log = AuditLog(path=tmp_path / "audit.log")
    log.append_event("A")
    log.append_event("B")
    assert log.verify_log()
    lines = (tmp_path / "audit.log").read_text().splitlines()
    lines[0] = lines[0].replace("A", "X")
    (tmp_path / "audit.log").write_text("\n".join(lines) + "\n")
    assert not log.verify_log()
