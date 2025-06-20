# tests/test_streaming_aead_edge.py
import os
import pytest

from src.streaming_aead import CHUNK, TAG_SZ, pack_stream, resume_decrypt, unpack_stream


def test_resume_decrypt_detects_final_tree_mac_mismatch(tmp_path):
    src = tmp_path / "in.bin"
    src.write_bytes(b"hello world" * 10)
    key = os.urandom(32)
    packed = tmp_path / "out.zst"
    pack_stream(src, packed, key)

    raw = bytearray(packed.read_bytes())
    # напрямую порти последний тег, чтобы сломать итоговое дерево MAC
    raw[-TAG_SZ] ^= 0xFF
    packed.write_bytes(raw)

    with pytest.raises(ValueError, match="MAC mismatch"):
        resume_decrypt(packed, key, have_bytes=packed.stat().st_size, out_path=tmp_path / "got.bin")


def test_unpack_stream_detects_silent_corruption(tmp_path):
    # две половинки чанка, чтобы было минимум 1 полный
    payload = b"A" * (CHUNK // 2) + b"B" * (CHUNK // 2)
    src = tmp_path / "foo.bin"
    src.write_bytes(payload)
    key = os.urandom(32)
    packed = tmp_path / "foo.zst"
    pack_stream(src, packed, key)

    raw = bytearray(packed.read_bytes())
    # портим первый байт зашифрованного блока
    idx = raw.find(b"\n\n") + 2 + 4  # конец заголовка + 4-байтная длина
    raw[idx] ^= 0xFF
    packed.write_bytes(raw)

    with pytest.raises(ValueError, match="MAC mismatch"):
        unpack_stream(packed, tmp_path / "out.bin", key)
