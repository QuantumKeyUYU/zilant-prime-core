import pytest

from container import get_metadata, pack_file, unpack_file, verify_integrity


class FakePQAEAD:
    _NONCE_LEN = 12

    @staticmethod
    def encrypt(pub, plaintext, aad=b""):
        # Вернём псевдопакет: nonce + ciphertext (имитация)
        return b"x" * FakePQAEAD._NONCE_LEN + plaintext + b"PQ"


def test_pack_file_with_pq_and_extra_meta(tmp_path, monkeypatch):
    import container

    monkeypatch.setattr(container, "PQAEAD", FakePQAEAD)
    src = tmp_path / "pq.txt"
    src.write_bytes(b"pqtest")
    pq_pub = b"x" * 32
    out = tmp_path / "pq.zil"
    pack_file(src, out, b"0" * 32, pq_public_key=pq_pub, extra_meta={"test": "meta"})
    assert out.exists()


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


def test_get_metadata_invalid_format(tmp_path):
    f = tmp_path / "broken.zil"
    # Нет разделителя HEADER_SEPARATOR — должен вызвать ошибку
    f.write_bytes(b"just some text, but no separator")
    with pytest.raises(ValueError, match="Invalid ZIL container format"):
        get_metadata(f)
