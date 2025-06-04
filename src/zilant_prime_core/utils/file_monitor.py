"""Watch critical files and exit if modified."""
from __future__ import annotations

import os
import sys
from pathlib import Path

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

__all__ = ["start_file_monitor"]


class _ExitOnChange(FileSystemEventHandler):  # type: ignore[misc]
    def __init__(self, files: list[str]) -> None:
        self.files = {os.path.abspath(f) for f in files}

    def on_any_event(self, event: FileSystemEvent) -> None:  # pragma: no cover - behaviour tested indirectly
        path = os.path.abspath(event.src_path)
        if path in self.files:
            sys.exit(1)


def start_file_monitor(files: list[str]) -> Observer:
    """Start watchdog observer for the given files."""
    observer = Observer()
    handler = _ExitOnChange(files)
    for f in files:
        observer.schedule(handler, Path(f).parent, recursive=False)
    observer.start()
    return observer
