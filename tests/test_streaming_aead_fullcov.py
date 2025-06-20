import json
import os
import pytest

from src.streaming_aead import pack_stream, resume_decrypt


def test_resume_decrypt_detects_root_tag_mismatch(tmp_path):
    """
    Тест на подделку root_tag: всё тело файла валидно,
    но в header подменён root_tag. Должно падать ровно на проверке дерева MAC (строка 211).
    """
    src = tmp_path / "input.bin"
    src.write_bytes(b"flying_potato" * 123)
    key = os.urandom(32)
    packed = tmp_path / "packed.zst"
    pack_stream(src, packed, key)

    # Подменяем root_tag только в header (всё остальное валидно!)
    data = packed.read_bytes()
    header, body = data.split(b"\n\n", 1)
    meta = json.loads(header.decode())
    meta["root_tag"] = "ff" * 32  # абсолютно неверный тег
    hacked = json.dumps(meta).encode() + b"\n\n" + body
    packed.write_bytes(hacked)

    # Ожидаем ровно ValueError на дереве MAC (211 строка)
    with pytest.raises(ValueError, match="MAC mismatch"):
        resume_decrypt(
            packed,
            key,
            have_bytes=packed.stat().st_size,
            out_path=tmp_path / "unpacked.bin",
        )
