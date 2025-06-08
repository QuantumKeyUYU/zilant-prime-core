from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable

__all__ = ["ScreenGuard", "SecurityError"]


class SecurityError(RuntimeError):
    """Raised when screen capture is detected."""


class ScreenGuard:
    def __init__(self) -> None:
        self._bad_processes: set[str] = {
            "obs",
            "obs.exe",
            "obs64.exe",
            "gnome-screenshot",
            "spectacle",
        }

    def _iter_process_names(self) -> Iterable[str]:
        import psutil

        for proc in psutil.process_iter(attrs=["name"]):
            name = proc.info.get("name")
            if name:
                yield name.lower()

    def _check_unix_video(self) -> bool:
        if sys.platform.startswith("linux"):
            for path in Path("/dev").glob("video*"):
                if path.exists() and path.stat().st_size > 0:
                    return True
        return False

    def assert_secure(self) -> None:
        if any(name in self._bad_processes for name in self._iter_process_names()):
            raise SecurityError("Screen recording software detected")
        if self._check_unix_video():
            raise SecurityError("/dev/video* in use")
