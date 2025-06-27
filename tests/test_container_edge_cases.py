import pytest

from container import pack_file, unpack_file, verify_integrity


def test_pack_file_with_pq_and_extra_meta(tmp_path):
    src = tmp_path / "pq.txt"
    src.write_bytes(b"pqtest")
    pq_pub = b"x" * 32
    # Попробуем сделать вызов с post-quantum public key
    try:
        pack_file(src, tmp_path / "pq.zil", b"0" * 32, pq_public_key=pq_pub, extra_meta={"test": "meta"})
        assert (tmp_path / "pq.zil").exists()
    except ImportError as e:
        pytest.skip(f"PQAEAD/Kyber768 backend not available: {e}")


def test_unpack_file_tamper_detected(monkeypatch, tmp_path):
    src = tmp_path / "bad.zil"
    src.write_bytes(b"BAD DATA")

    def fake_record(*a, **k):
        raise RuntimeError("fail")

    monkeypatch.setattr("audit_ledger.record_action", fake_record)
    with pytest.raises(ValueError):
        unpack_file(src, tmp_path / "o", b"0" * 32)


def test_verify_integrity_broken_magic(tmp_path):
    src = tmp_path / "f.zil"
    src.write_bytes(b'{"magic":"FAIL","version":1}\n\npayload')
    assert not verify_integrity(src)


def test_verify_integrity_broken_version(tmp_path):
    src = tmp_path / "f2.zil"
    src.write_bytes(b'{"magic":"ZILANT","version":42}\n\npayload')
    assert not verify_integrity(src)


def test_verify_integrity_invalid_json(tmp_path):
    src = tmp_path / "f3.zil"
    src.write_bytes(b"{INVALIDJSON}\n\npayload")
    assert not verify_integrity(src)
