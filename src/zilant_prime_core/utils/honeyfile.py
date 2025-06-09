from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path

__all__ = ["HoneyfileError", "check_tmp_for_honeyfiles"]


class HoneyfileError(Exception):
    """Raised when a honeyfile is detected."""


def check_tmp_for_honeyfiles(tmp_dir: Path | str | None = None) -> None:
    dir_path = Path(tmp_dir or tempfile.gettempdir())
    for p in dir_path.glob("*"):
        if p.suffix.lower() in {".doc", ".pdf"}:
            # simple hash trap
            try:
                digest = hashlib.sha256(p.read_bytes()).hexdigest()
            except Exception:
                digest = ""
            raise HoneyfileError(f"Honeyfile detected: {p.name} ({digest})")
