"""
Распаковка `.zil`-контейнера (ZIP) обратно на диск.
"""

from __future__ import annotations

import shutil
import tempfile
import zipfile
from pathlib import Path


def unpack(zil_path: str | Path, output_path: str | Path | None = None) -> None:
    src = Path(zil_path)
    if not src.exists():
        raise FileNotFoundError(src)

    dst = Path(output_path) if output_path else src.with_suffix("")
    dst.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        z_tmp = Path(tmp) / "data.zip"
        shutil.copy(src, z_tmp)
        with zipfile.ZipFile(z_tmp, "r") as zf:
            zf.extractall(dst)
