"""
Обратная операция к `pack` ― извлечение Zip-архива в каталог назначения.
"""

from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Sequence

__all__ = ["unpack", "UnpackError"]


class UnpackError(RuntimeError):
    """Невалидный Zip или ошибки на диске."""


def unpack(archive: Path, dest: Path, password: str) -> Sequence[str]:  # noqa: ARG001
    try:
        with zipfile.ZipFile(archive, "r") as zf:
            zf.extractall(dest)
            return zf.namelist()
    except Exception as exc:  # pragma: no cover
        raise UnpackError(str(exc)) from exc
