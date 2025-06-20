import json
import os
import pytest

from src.streaming_aead import pack_stream, resume_decrypt


def test_resume_decrypt_fails_on_invalid_root_tag(tmp_path):
    # Создаём валидный контейнер
    src = tmp_path / "orig.bin"
    src.write_bytes(b"magic cryptotest data" * 10)
    key = os.urandom(32)
    packed = tmp_path / "valid.zst"
    pack_stream(src, packed, key)

    # Ломаем root_tag: декодим заголовок, подменяем root_tag, пересобираем файл
    raw = packed.read_bytes()
    header, body = raw.split(b"\n\n", 1)
    meta = json.loads(header.decode())
    meta["root_tag"] = "00" * 32  # некорректный root_tag
    corrupted = json.dumps(meta).encode() + b"\n\n" + body
    packed.write_bytes(corrupted)

    # Дешифрация должна завершиться именно на проверке root_tag
    with pytest.raises(ValueError, match="MAC mismatch"):
        resume_decrypt(packed, key, have_bytes=packed.stat().st_size, out_path=tmp_path / "out.bin")
