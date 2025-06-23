# SPDX-License-Identifier: MIT
"""File monitor that triggers self-healing reactions."""

from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any

# watchdog is optional and imported lazily to avoid hard dependency
try:  # pragma: no cover - optional
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer
except Exception:  # pragma: no cover - missing watchdog
    FileSystemEventHandler = object  # type: ignore
    Observer = None

from zilant_prime_core.zkp import prove_intact

from .reaction import maybe_self_destruct, record_event, rotate_key


class _Handler(FileSystemEventHandler):
    def __init__(self, path: Path) -> None:
        self.path = path

    def on_modified(self, event: Any) -> None:  # pragma: no cover - integration
        if getattr(event, "src_path", None) == str(self.path):
            rotate_key(b"initial-key".ljust(32, b"\0"))
            record_event({"file": str(self.path), "action": "modified"})
            prove_intact(hashlib.sha3_256(str(self.path).encode()).digest())
            maybe_self_destruct(self.path)


def monitor_container(path: str) -> None:
    """Watch *path* for modifications and trigger reactions."""
    if Observer is None:
        raise ImportError("watchdog is required for monitor_container")

    p = Path(path)
    handler = _Handler(p)
    observer = Observer()
    observer.schedule(handler, p.parent.as_posix(), recursive=False)
    observer.start()
    try:
        while observer.is_alive():
            time.sleep(0.1)
    finally:
        observer.stop()
        observer.join()


__all__ = ["monitor_container"]
