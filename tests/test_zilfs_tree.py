import hashlib
import shutil
from pathlib import Path

import pytest

from zilant_prime_core.zilfs import ZilantFS, unpack_dir

pytestmark = pytest.mark.zilfs


def _hash_tree(path: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(path.rglob("*")):
        if p.is_file():
            h.update(p.read_bytes())
    return h.hexdigest()


def test_zilfs_tree_roundtrip(tmp_path: Path) -> None:
    src = tmp_path / "src"
    (src / "dir").mkdir(parents=True)
    (src / "dir" / "a.txt").write_text("alpha")
    (src / "b.bin").write_bytes(b"b" * 10)

    container = tmp_path / "c.zil"
    fs = ZilantFS(container, b"x" * 32)
    shutil.copytree(src, fs.root, dirs_exist_ok=True)
    fs.destroy("/")

    out = tmp_path / "out"
    unpack_dir(container, out, b"x" * 32)
    assert _hash_tree(src) == _hash_tree(out)
