"""Minimal stub of _winapi for non-Windows tests."""
from typing import Any

def CopyFile2(src: str, dst: str, flags: int = 0, progress: Any | None = None) -> int:
    """Simple replacement that copies file contents."""
    import shutil
    shutil.copy2(src, dst)
    return 0
