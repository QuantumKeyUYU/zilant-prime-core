# src/pack.py

"""
Простейшая упаковка в .zil-контейнер (ZIP).
Поддерживает stub-параметры password, vdf_iters, meta, one_shot.
"""

import shutil
import tempfile
import zipfile

from pathlib import Path
from typing import Any, Dict, Optional


def _zip_dir(src: Path, zf: zipfile.ZipFile) -> None:
    for p in src.rglob("*"):
        if p.is_file():
            zf.write(p, arcname=p.relative_to(src))


def pack(
    input_path: str | Path,
    output_path: str | Path,
    password: Optional[str] = None,
    vdf_iters: int = 0,
    meta: Optional[Dict[str, str]] = None,
    one_shot: bool = False,
) -> None:
    """
    Упаковать файл/папку в `.zil` (ZIP).
    Параметры password, vdf_iters и meta игнорируются в stub.
    """
    inp = Path(input_path)
    out = Path(output_path).with_suffix(".zil")

    if not inp.exists():
        raise FileNotFoundError(inp)

    with tempfile.TemporaryDirectory() as tmp:
        z_tmp = Path(tmp) / "data.zip"
        with zipfile.ZipFile(z_tmp, "w", zipfile.ZIP_DEFLATED) as zf:
            if inp.is_dir():
                _zip_dir(inp, zf)
            else:
                zf.write(inp, arcname=inp.name)
        shutil.copy(z_tmp, out)


def one_shot_pack(
    input_path: str | Path,
    output_path: str | Path,
    password: Optional[str] = None,
    vdf_iters: int = 0,
    meta: Optional[Dict[str, str]] = None,
    **kwargs: Any,
) -> None:
    """
    Одношотная упаковка (stub): совпадает с обычной pack.
    """
    pack(input_path, output_path, password, vdf_iters, meta, one_shot=True)
