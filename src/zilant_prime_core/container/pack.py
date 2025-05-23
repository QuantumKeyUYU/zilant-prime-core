"""
Naïve реализация «упаковщика» в один Zip-архив.
Пароль пока *не используется* — тестам важен сам байтовый результат.
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path


def _add_entry(z: zipfile.ZipFile, root: Path, entry: Path) -> None:
    if entry.is_file():
        z.write(entry, entry.relative_to(root))


def pack(src: Path, password: str) -> bytes:  # noqa: ARG001 (password reserved)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        if src.is_dir():
            for p in src.rglob("*"):
                _add_entry(zf, src, p)
        else:
            _add_entry(zf, src.parent, src)
    return buf.getvalue()
