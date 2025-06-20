import json
import os
import pytest

from src.streaming_aead import pack_stream, resume_decrypt


def test_resume_decrypt_tree_mac_check(tmp_path):
    # Готовим валидный контейнер
    src = tmp_path / "data.bin"
    src.write_bytes(b"Abracadabra " * 100)
    key = os.urandom(32)
    packed = tmp_path / "archived.zst"
    pack_stream(src, packed, key)

    # Ломаем только root_tag, чтобы декодинг и декомпрессия были валидны, но финальный MAC-tree не совпал
    raw = packed.read_bytes()
    header, body = raw.split(b"\n\n", 1)
    meta = json.loads(header.decode())
    meta["root_tag"] = "00" * 32  # Invalid root tag
    corrupted = json.dumps(meta).encode() + b"\n\n" + body
    packed.write_bytes(corrupted)

    # Проверяем: должно падать ровно на финальном чекере дерева MAC
    with pytest.raises(ValueError, match="MAC mismatch"):
        resume_decrypt(packed, key, have_bytes=packed.stat().st_size, out_path=tmp_path / "out.bin")
