import pytest
import sys
from pathlib import Path

if sys.platform == "win32":
    pytest.skip("mkfifo/NamedPipe отсутствует под Windows", allow_module_level=True)

from zilant_prime_core.zilfs import ZilantFS, unpack_dir

pytestmark = pytest.mark.zilfs


def _hash_file(path: Path) -> str:
    import hashlib

    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def test_zilfs_stream_big(tmp_path: Path, monkeypatch):
    src = tmp_path / "src"
    src.mkdir()
    big = src / "big.bin"
    with open(big, "wb") as fh:
        fh.truncate(6 * 1024 * 1024 * 1024)
    container = tmp_path / "c.zil"
    monkeypatch.setenv("ZILANT_STREAM", "1")
    fs = ZilantFS(container, b"k" * 32)
    import shutil

    shutil.copy2(big, fs.root / "big.bin")
    fs.destroy("/")
    out = tmp_path / "out"
    unpack_dir(container, out, b"k" * 32)
    assert _hash_file(big) == _hash_file(out / "big.bin")
