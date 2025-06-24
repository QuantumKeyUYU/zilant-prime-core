# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

# src/zilant_prime_core/container/__init__.py

try:
    from container import HEADER_SEPARATOR, get_metadata
    from container import pack as _pack
    from container import pack_file, unpack_file, verify_integrity
except ModuleNotFoundError:  # pragma: no cover - installed as package
    HEADER_SEPARATOR = b"\n\n"
    from .pack import pack as _pack

    def pack_file(*_a: object, **_kw: object) -> None:
        """Stub for pack_file when standalone module is unavailable."""
        raise NotImplementedError("pack_file is unavailable")

    def unpack_file(*_a: object, **_kw: object) -> None:
        """Stub for unpack_file when standalone module is unavailable."""
        raise NotImplementedError("unpack_file is unavailable")

    def get_metadata(*_a: object, **_kw: object) -> dict[str, object]:
        """Stub for get_metadata when standalone module is unavailable."""
        raise NotImplementedError("get_metadata is unavailable")

    def verify_integrity(*_a: object, **_kw: object) -> bool:
        """Stub for verify_integrity when standalone module is unavailable."""
        raise NotImplementedError("verify_integrity is unavailable")

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
