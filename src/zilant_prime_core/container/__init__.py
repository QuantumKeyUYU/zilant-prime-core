# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

# src/zilant_prime_core/container/__init__.py

from typing import Any, cast

try:
    import container as _ext

    if not callable(getattr(_ext, "pack", None)):
        raise ModuleNotFoundError
    HEADER_SEPARATOR = _ext.HEADER_SEPARATOR
    get_metadata = _ext.get_metadata  # type: ignore[assignment]
    _selected_pack = cast(Any, _ext.pack)
    pack_file = _ext.pack_file  # type: ignore[assignment]
    unpack_file = _ext.unpack_file  # type: ignore[assignment]
    verify_integrity = _ext.verify_integrity  # type: ignore[assignment]
    from container import unpack as _unused_unpack  # noqa: F401
except Exception:  # pragma: no cover - installed as package
    HEADER_SEPARATOR = b"\n\n"
    from .metadata import get_metadata  # type: ignore
    from .pack import pack as _fallback_pack

    _selected_pack = cast(Any, _fallback_pack)

from .metadata import MetadataError
from .unpack import unpack

if "pack_file" not in globals():

    def pack_file(*args: Any, **kwargs: Any) -> None:
        raise NotImplementedError("pack_file is unavailable")

    def unpack_file(*args: Any, **kwargs: Any) -> None:
        raise NotImplementedError("unpack_file is unavailable")

    def verify_integrity(*args: Any, **kwargs: Any) -> bool:
        raise NotImplementedError("verify_integrity is unavailable")


pack = _selected_pack

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
