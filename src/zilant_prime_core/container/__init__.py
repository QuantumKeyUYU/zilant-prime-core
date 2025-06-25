# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

"""Container helpers and fallbacks."""

try:
    from container import HEADER_SEPARATOR, get_metadata
    from container import pack as _pack
    from container import pack_file, unpack_file, verify_integrity
except Exception:  # pragma: no cover - fallback to bundled modules
    HEADER_SEPARATOR = b"\n\n"
    try:
        from .metadata import get_metadata  # type: ignore
        from .pack import pack as _pack  # type: ignore
        from .pack import pack_file  # type: ignore
        from .unpack import unpack_file, verify_integrity  # type: ignore
    except Exception:

        def _pack(*_a: object, **_kw: object) -> bytes:
            raise NotImplementedError("pack is unavailable")

        def pack_file(*_a: object, **_kw: object) -> None:
            raise NotImplementedError("pack_file is unavailable")

        def unpack_file(*_a: object, **_kw: object) -> None:
            raise NotImplementedError("unpack_file is unavailable")

        def get_metadata(*_a: object, **_kw: object) -> dict[str, object]:
            raise NotImplementedError("get_metadata is unavailable")

        def verify_integrity(*_a: object, **_kw: object) -> bool:
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
