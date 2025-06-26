# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

# src/zilant_prime_core/container/__init__.py

try:
    from container import HEADER_SEPARATOR  # type: ignore[attr-defined]
    from container import get_metadata  # type: ignore[attr-defined]
    from container import pack_file  # type: ignore[attr-defined,no-redef]
    from container import pack as _pack
    from container import unpack_file, verify_integrity  # type: ignore[attr-defined,no-redef]
except ModuleNotFoundError:  # pragma: no cover - installed as package
    HEADER_SEPARATOR = b"\n\n"
    from .metadata import get_metadata  # type: ignore
    from .pack import pack as _pack  # type: ignore[assignment]
    from .pack import pack_file  # type: ignore[attr-defined,no-redef]
    from .unpack import unpack_file, verify_integrity  # type: ignore
else:
    from container import unpack as _unused_unpack  # noqa: F401

from .metadata import MetadataError
from .unpack import unpack

pack = _pack  # type: ignore[assignment]

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
