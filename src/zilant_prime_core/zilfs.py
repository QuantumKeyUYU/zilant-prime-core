from __future__ import annotations

import errno
import os
import stat
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

try:
    from fuse import FUSE, FuseOSError, Operations  # type: ignore
except Exception:  # pragma: no cover - optional dependency may be missing
    FUSE = None  # type: ignore[assignment]
    FuseOSError = OSError  # type: ignore[misc]

    class _Operations:
        pass

    Operations = _Operations


from container import pack_file, unpack_file


class ZilantFS(Operations):
    """Simple FUSE filesystem that maps a single encrypted file."""

    def __init__(self, container: Path, password: bytes) -> None:
        self.container = Path(container)
        self.password = password
        self._tmp = TemporaryDirectory()
        self.file_name = "data"
        self.file_path = Path(self._tmp.name) / self.file_name
        if self.container.exists():
            unpack_file(self.container, self.file_path, self.password)
        else:
            self.file_path.touch()

    # ------------------------- helpers -------------------------
    def _file_stat(self) -> os.stat_result:
        return os.lstat(self.file_path)

    # ------------------------- FUSE API -------------------------
    def destroy(self, path: str) -> None:  # pragma: no cover - called on unmount
        pack_file(self.file_path, self.container, self.password)
        self._tmp.cleanup()

    def getattr(self, path: str, fh: int | None = None) -> dict[str, Any]:
        if path == "/":
            return dict(st_mode=(stat.S_IFDIR | 0o755), st_nlink=2)
        if path == f"/{self.file_name}":
            st = self._file_stat()
            return dict(st_mode=(stat.S_IFREG | 0o644), st_nlink=1, st_size=st.st_size)
        raise FuseOSError(errno.ENOENT)

    def readdir(self, path: str, fh: int) -> list[str]:  # pragma: no cover - trivial
        if path != "/":
            raise FuseOSError(errno.ENOENT)
        return [".", "..", self.file_name]

    def open(self, path: str, flags: int) -> int:
        if path != f"/{self.file_name}":
            raise FuseOSError(errno.ENOENT)
        return os.open(self.file_path, flags)

    def create(self, path: str, mode: int, fi: Any | None = None) -> int:
        if path != f"/{self.file_name}":
            raise FuseOSError(errno.EPERM)
        return os.open(self.file_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, mode)

    def read(self, path: str, size: int, offset: int, fh: int) -> bytes:
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, size)

    def write(self, path: str, data: bytes, offset: int, fh: int) -> int:
        os.lseek(fh, offset, os.SEEK_SET)
        return os.write(fh, data)

    def truncate(self, path: str, length: int) -> None:
        with open(self.file_path, "r+b") as fh:
            fh.truncate(length)

    def flush(self, path: str, fh: int) -> None:  # pragma: no cover - passthrough
        os.fsync(fh)

    def release(self, path: str, fh: int) -> None:  # pragma: no cover - passthrough
        os.close(fh)


def mount_fs(container: Path, mountpoint: Path, password: str, *, foreground: bool = True) -> None:
    """Mount CONTAINER on MOUNTPOINT."""
    if FUSE is None:
        raise RuntimeError("fusepy is not installed")
    mountpoint.mkdir(parents=True, exist_ok=True)
    fs = ZilantFS(container, password.encode())
    FUSE(fs, str(mountpoint), foreground=foreground)


def umount_fs(mountpoint: Path) -> None:
    """Unmount MOUNTPOINT."""
    if os.name == "nt":
        subprocess.run(["fsutil", "volume", "dismount", str(mountpoint)], check=True)
    else:
        subprocess.run(["fusermount", "-u", str(mountpoint)], check=True)
