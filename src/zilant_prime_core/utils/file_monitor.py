"""Watch critical files and exit if modified."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

# TODO: реализовать heartbeats parent-child
# TODO: добавить FileLock или flock для бинаря

__all__ = ["start_file_monitor"]


class _ExitOnChange(FileSystemEventHandler):  # type: ignore[misc]
    def __init__(self, files: list[str]) -> None:
        self.files = {os.path.abspath(f) for f in files}

    def on_any_event(self, event: FileSystemEvent) -> None:  # pragma: no cover - behaviour tested indirectly
        path = os.path.abspath(event.src_path)
        if path in self.files:
            sys.exit(1)


from typing import Any, cast


class _DummyObserver:
    """Fallback observer used when watchdog cannot start."""

    def stop(self) -> None:  # pragma: no cover - behaviour trivial
        pass

    def join(self, timeout: float | None = None) -> None:  # pragma: no cover
        pass


def start_file_monitor(files: list[str]) -> Any:
    """Start watchdog observer for the given files.

    If the observer cannot be started (e.g. missing platform support), a dummy
    observer that exposes ``stop`` and ``join`` is returned instead of raising an
    exception.  This mirrors the expected interface but performs no monitoring.
    """

    try:
        observer: Any = Observer()
        handler = _ExitOnChange(files)
        for f in files:
            cast(Any, observer).schedule(handler, Path(f).parent, recursive=False)
        cast(Any, observer).start()
        return observer
    except Exception:  # pragma: no cover - platform dependent
        return _DummyObserver()
