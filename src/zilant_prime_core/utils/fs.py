"""Cross-platform file system helpers."""

from __future__ import annotations

import os
import sys

if sys.platform == "win32":  # pragma: no cover - Windows fallback
    if not hasattr(os, "mkfifo"):

        def _noop(*_a: object, **_kw: object) -> None:
            """No-op placeholder for missing POSIX APIs."""
            return None

        os.mkfifo = _noop  # type: ignore[attr-defined]
    if not hasattr(os, "sync"):

        def _noop_sync() -> None:
            return None

        os.sync = _noop_sync  # type: ignore[attr-defined]

__all__ = ["os"]
