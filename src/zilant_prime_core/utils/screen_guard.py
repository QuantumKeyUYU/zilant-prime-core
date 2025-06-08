from __future__ import annotations

import sys
from typing import Iterable

__all__ = ["ScreenGuard", "ScreenGuardError", "guard"]


class ScreenGuardError(Exception):
    """Raised when screen recording is detected."""


class ScreenGuard:
    def __init__(self) -> None:
        try:
            import psutil

            self._psutil = psutil
        except ImportError:
            self._psutil = None
        self._bad_processes: set[str] = {"obs", "obs.exe", "ffmpeg"}

    def _iter_proc_names(self) -> Iterable[str]:
        if not self._psutil:
            return
        for proc in self._psutil.process_iter(attrs=["name"]):
            name = proc.info.get("name")
            if name:
                yield name.lower()

    def assert_secure(self) -> None:
        if not self._psutil:
            return
        for name in self._iter_proc_names():
            if any(bad in name for bad in self._bad_processes):
                raise ScreenGuardError(f"Screen recording detected: {name}")
        if sys.platform.startswith("linux"):
            for proc in self._psutil.process_iter(attrs=["open_files"]):
                for f in proc.info.get("open_files") or []:
                    path = getattr(f, "path", "")
                    if path.startswith("/dev/video"):
                        raise ScreenGuardError("Webcam or screen-capture device in use")


# global instance
guard = ScreenGuard()
