# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

"""Container helpers with local fallbacks."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

try:  # prefer standalone container module if available
    from container import HEADER_SEPARATOR as HEADER_SEPARATOR
    from container import get_metadata
    from container import pack as _pack
    from container import pack_file, unpack, unpack_file, verify_integrity

    from .metadata import MetadataError
except Exception:  # pragma: no cover - fallback to bundled modules
    HEADER_SEPARATOR = b"\n\n"
    from .metadata import MetadataError

    def _pack(*_a: object, **_kw: object) -> bytes:
        raise NotImplementedError("pack is unavailable")

    def pack_file(*_a: object, **_kw: object) -> None:
        raise NotImplementedError("pack_file is unavailable")

    def unpack_file(*_a: object, **_kw: object) -> None:
        raise NotImplementedError("unpack_file is unavailable")

    def verify_integrity(*_a: object, **_kw: object) -> bool:
        raise NotImplementedError("verify_integrity is unavailable")

    def unpack(*_a: object, **_kw: object) -> tuple[dict[str, Any], bytes]:
        raise NotImplementedError("unpack is unavailable")


pack = _pack

__all__ = [
    "MetadataError",
    "HEADER_SEPARATOR",
    "pack",
    "unpack",
    "pack_file",
    "unpack_file",
    "get_metadata",
    "verify_integrity",
]
