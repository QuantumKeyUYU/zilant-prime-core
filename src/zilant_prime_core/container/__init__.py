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
    from .pack import pack as _pack
    from .pack import pack as pack_file
    from .unpack import unpack_file, verify_integrity  # type: ignore
else:
    from container import unpack as _unused_unpack  # noqa: F401

from .metadata import MetadataError
from .unpack import unpack

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
