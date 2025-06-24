# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

# src/zilant_prime_core/container/__init__.py

try:
    from container import HEADER_SEPARATOR, get_metadata
    from container import pack as _pack
    from container import pack_file, unpack_file, verify_integrity
except ModuleNotFoundError:  # pragma: no cover - installed as package
    HEADER_SEPARATOR = b"\n\n"
    from .metadata import get_metadata  # type: ignore
    from .pack import pack as _pack  # type: ignore[assignment]
else:
    from container import unpack as _unused_unpack  # noqa: F401

from .metadata import MetadataError
from .unpack import unpack

if "pack_file" not in globals():
    from typing import Any

    def pack_file(*args: Any, **kwargs: Any) -> None:
        raise NotImplementedError("pack_file is unavailable")

    def unpack_file(*args: Any, **kwargs: Any) -> None:
        raise NotImplementedError("unpack_file is unavailable")

    def verify_integrity(*args: Any, **kwargs: Any) -> bool:
        raise NotImplementedError("verify_integrity is unavailable")


pack = _pack

__all__ = [
    "HEADER_SEPARATOR",
    "MetadataError",
    "get_metadata",
    "pack",
    "pack_file",
    "unpack",
    "unpack_file",
    "verify_integrity",
]
