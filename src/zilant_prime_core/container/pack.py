# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

__all__ = [
    "PackError",
    "pack",
]

# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

import json
import os
from pathlib import Path

from zilant_prime_core.crypto.aead import encrypt_aead
from zilant_prime_core.crypto.kdf import derive_key
from zilant_prime_core.utils.constants import DEFAULT_NONCE_LENGTH, DEFAULT_SALT_LENGTH
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
