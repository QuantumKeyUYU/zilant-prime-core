# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

# src/zilant_prime_core/container/__init__.py

try:
    from container import HEADER_SEPARATOR, get_metadata, pack_file, unpack_file, verify_integrity
except ModuleNotFoundError:  # pragma: no cover - installed as package
    from . import pack_file, unpack_file  # circular placeholder - not expected

from .metadata import MetadataError
from .pack import pack
from .unpack import unpack

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
