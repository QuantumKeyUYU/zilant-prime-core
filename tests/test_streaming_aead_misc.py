# tests/test_streaming_aead_misc.py

import os
import pytest

import streaming_aead as sa


def test_unpack_verify_only(tmp_path):
    # pack небольшой файл
    data = b"hello world" * 10
    src = tmp_path / "src.bin"
    src.write_bytes(data)
    key = os.urandom(32)
    packed = tmp_path / "c.zst"
    sa.pack_stream(src, packed, key)

    out = tmp_path / "out.bin"
    # verify_only=True, progress=True → не создаёт файл
    sa.unpack_stream(packed, out, key, verify_only=True, progress=True)
    assert not out.exists()


def test_unpack_offset(tmp_path, monkeypatch):
    # уменьшаем CHUNK, чтобы получить несколько чанков
    import streaming_aead as sa_mod

    monkeypatch.setattr(sa_mod, "CHUNK", 10)
    data = b"A" * 50
    src = tmp_path / "src.bin"
    src.write_bytes(data)
    key = os.urandom(32)
    packed = tmp_path / "c2.zst"
    sa_mod.pack_stream(src, packed, key)

    out = tmp_path / "out2.bin"
    # offset большая — все чанки пропущены, файл пустой
    sa_mod.unpack_stream(packed, out, key, offset=10**6)
    assert out.exists()
    assert out.read_bytes() == b""


def test_unpack_truncated_header_json(tmp_path):
    # некорректный JSON в заголовке → JSONDecodeError → ValueError("truncated header")
    bad = tmp_path / "bad.zst"
    bad.write_bytes(b"notjson\n\n")
    with pytest.raises(ValueError, match="truncated header"):
        sa.unpack_stream(bad, tmp_path / "o.bin", os.urandom(32))


def test_unpack_mac_mismatch(tmp_path):
    # повреждаем контейнер для проверки MAC-броска
    data = b"secret!" * 5
    src = tmp_path / "in.bin"
    src.write_bytes(data)
    key = os.urandom(32)
    packed = tmp_path / "bad_mac.zst"
    sa.pack_stream(src, packed, key)

    raw = bytearray(packed.read_bytes())
    # инвертируем один байт первого чанка
    hdr_end = raw.find(b"\n\n") + 2
    # пропускаем header, 4 байта длины
    idx = hdr_end + 4
    raw[idx] ^= 0xFF
    packed.write_bytes(raw)

    out = tmp_path / "out3.bin"
    with pytest.raises(ValueError, match="MAC mismatch"):
        sa.unpack_stream(packed, out, key)


def test_resume_decrypt_truncated_header(tmp_path):
    # пустой файл → resume_decrypt поймает "truncated header"
    stub = tmp_path / "stub.zst"
    stub.write_bytes(b"")
    with pytest.raises(ValueError, match="truncated header"):
        sa.resume_decrypt(stub, os.urandom(32), have_bytes=10**6, out_path=tmp_path / "o.bin")
