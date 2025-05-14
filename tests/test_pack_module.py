"""
Cover src/zilant_prime_core/container/pack.py + unpack.py.
"""
from pathlib import Path

import pytest

from zilant_prime_core.container import pack, unpack


def test_pack_unpack_roundtrip(tmp_path: Path):
    # ── подготовка исходного файла ──
    src = tmp_path / "dragon.raw"
    payload = b"DRACARYS"
    src.write_bytes(payload)

    # ── pack() в «памяти» ──
    container = pack(src, password="🔥")

    # ── распаковываем из bytes → директория ──
    out_dir = tmp_path / "out"
    out_file = unpack(container, output_dir=out_dir, password="🔥")
    assert out_file.read_bytes() == payload
    assert out_file.name == src.name

    # ── негативный сценарий: повторная распаковка запрещена ──
    with pytest.raises(FileExistsError):
        unpack(container, output_dir=out_dir, password="🔥")
