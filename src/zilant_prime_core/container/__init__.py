# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

# src/zilant_prime_core/container/__init__.py


from container import HEADER_SEPARATOR, get_metadata
from container import pack as _pack
from container import pack_file
from container import unpack as _unused_unpack  # noqa: F401
from container import unpack_file, verify_integrity

from .metadata import MetadataError
from .unpack import unpack

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
