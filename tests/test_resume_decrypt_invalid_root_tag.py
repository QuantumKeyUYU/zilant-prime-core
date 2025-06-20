import json
import os
import pytest

from src.streaming_aead import pack_stream, resume_decrypt


def test_resume_decrypt_invalid_root_tag(tmp_path):
    # 1. Создать валидный контейнер
    src = tmp_path / "in.bin"
    src.write_bytes(b"testdata" * 32)
    key = os.urandom(32)
    packed = tmp_path / "packed.zst"
    pack_stream(src, packed, key)

    # 2. Считать файл, разделить на header и body
    data = packed.read_bytes()
    header, body = data.split(b"\n\n", 1)
    meta = json.loads(header.decode())
    # 3. Подменить root_tag на фиктивный
    meta["root_tag"] = "00" * 32
    # 4. Склеить header и body, записать обратно
    hacked = json.dumps(meta).encode() + b"\n\n" + body
    packed.write_bytes(hacked)

    # 5. Проверить, что ошибка ловится на проверке root_tag
    with pytest.raises(ValueError, match="MAC mismatch"):
        resume_decrypt(packed, key, have_bytes=packed.stat().st_size, out_path=tmp_path / "out.bin")
