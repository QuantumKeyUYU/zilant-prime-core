# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

# src/zilant_prime_core/container/__init__.py

from .metadata import MetadataError, get_metadata

HEADER_SEPARATOR = b"\n\n"
from .pack import pack
from .unpack import unpack, unpack_file, verify_integrity

pack_file = pack

__all__ = [
    "MetadataError",
    "get_metadata",
    "HEADER_SEPARATOR",
    "pack",
    "unpack",
    "pack_file",
    "unpack_file",
    "verify_integrity",
]
