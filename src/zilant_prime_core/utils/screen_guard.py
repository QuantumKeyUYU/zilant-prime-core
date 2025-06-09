# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors


class ScreenGuardError(Exception):
    pass


class ScreenGuard:
    _BLACKLIST = {"obs", "obs.exe", "ffmpeg", "ffmpeg.exe"}

    def __init__(self):
        try:
            import psutil

            self._psutil = psutil
        except ImportError:
            self._psutil = None

    def _iter_proc_names(self):
        if not self._psutil:
            return []
        for proc in self._psutil.process_iter(attrs=["name"]):
            try:
                name = (getattr(proc, "info", {}).get("name") or "").lower()
            except Exception:
                continue
            if name:
                yield name

    def assert_secure(self):
        for name in self._iter_proc_names():
            if name in self._BLACKLIST or any(name.endswith(x) for x in self._BLACKLIST):
                raise ScreenGuardError(f"Screen capture tool detected: {name}")


guard = ScreenGuard()
