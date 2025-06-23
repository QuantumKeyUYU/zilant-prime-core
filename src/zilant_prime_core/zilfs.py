from __future__ import annotations

import errno
import os
import subprocess
import tarfile
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Dict

try:  # pragma: no cover - optional dependency may be missing
    from fuse import FUSE, FuseOSError, Operations  # type: ignore
except Exception:  # pragma: no cover - optional dependency may be missing
    FUSE = None  # type: ignore[assignment]
    FuseOSError = OSError  # type: ignore[misc]

    class _Operations:
        pass

    Operations = _Operations

from container import pack_file, unpack_file
from utils.logging import get_logger


logger = get_logger("zilfs")

_DECOY_PROFILES: Dict[str, Dict[str, str]] = {"minimal": {"dummy.txt": "lorem ipsum", "pics/kitten.jpg": "PLACEHOLDER"}}


def pack_dir(src: Path, dest: Path, key: bytes) -> None:
    """Pack directory *src* into encrypted container *dest*."""
    with TemporaryDirectory() as tmp:
        tar_path = Path(tmp) / "data.tar"
        with tarfile.open(tar_path, "w") as tar:
            tar.add(src, arcname=".")
        pack_file(tar_path, dest, key)


def unpack_dir(container: Path, dest: Path, key: bytes) -> None:
    """Unpack encrypted container *container* into directory *dest*."""
    with TemporaryDirectory() as tmp:
        tar_path = Path(tmp) / "data.tar"
        unpack_file(container, tar_path, key)
        with tarfile.open(tar_path, "r") as tar:
            tar.extractall(dest)


class ZilantFS(Operations):
    """Simple FUSE filesystem exposing a directory tree."""

    def __init__(self, container: Path, password: bytes, *, decoy_profile: str | None = None) -> None:
        self.container = Path(container)
        self.password = password
        self.ro = False
        self._tmp = TemporaryDirectory()
        self.root = Path(self._tmp.name)
        if decoy_profile:
            self.ro = True
            self._populate_decoy(decoy_profile)
        elif self.container.exists():
            try:
                unpack_dir(self.container, self.root, self.password)
            except Exception as exc:  # pragma: no cover - integrity error
                logger.warning("integrity_error:%s", exc)
                self.ro = True
                try:
                    unpack_dir(self.container, self.root, self.password)
                except Exception:
                    pass
        else:
            self.root.mkdir(parents=True, exist_ok=True)

    # ------------------------- helpers -------------------------
    def _full_path(self, path: str) -> str:
        return str(self.root / path.lstrip("/"))

    def _check_rw(self) -> None:
        if self.ro:
            raise FuseOSError(errno.EACCES)

    # ------------------------- FUSE API -------------------------
    def destroy(self, path: str) -> None:  # pragma: no cover - called on unmount
        if not self.ro:
            pack_dir(self.root, self.container, self.password)
        self._tmp.cleanup()

    def getattr(self, path: str, fh: int | None = None) -> dict[str, Any]:
        st = os.lstat(self._full_path(path))
        return dict(
            (key, getattr(st, key))
            for key in ("st_atime", "st_ctime", "st_gid", "st_mode", "st_mtime", "st_nlink", "st_size", "st_uid")
        )

    def readdir(self, path: str, fh: int) -> list[str]:  # pragma: no cover - trivial
        full = self._full_path(path)
        return [".", "..", *os.listdir(full)]

    def open(self, path: str, flags: int) -> int:
        return os.open(self._full_path(path), flags)

    def create(self, path: str, mode: int, fi: Any | None = None) -> int:
        self._check_rw()
        return os.open(self._full_path(path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, mode)

    def read(self, path: str, size: int, offset: int, fh: int) -> bytes:
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, size)

    def write(self, path: str, data: bytes, offset: int, fh: int) -> int:
        self._check_rw()
        os.lseek(fh, offset, os.SEEK_SET)
        return os.write(fh, data)

    def truncate(self, path: str, length: int) -> None:
        self._check_rw()
        with open(self._full_path(path), "r+b") as fh:
            fh.truncate(length)

    def unlink(self, path: str) -> None:  # pragma: no cover - rare
        self._check_rw()
        os.unlink(self._full_path(path))

    def mkdir(self, path: str, mode: int) -> None:  # pragma: no cover - rare
        self._check_rw()
        os.mkdir(self._full_path(path), mode)

    def rmdir(self, path: str) -> None:  # pragma: no cover - rare
        self._check_rw()
        os.rmdir(self._full_path(path))

    def rename(self, old: str, new: str) -> None:  # pragma: no cover - rare
        self._check_rw()
        os.rename(self._full_path(old), self._full_path(new))

    def flush(self, path: str, fh: int) -> None:  # pragma: no cover - passthrough
        os.fsync(fh)

    def release(self, path: str, fh: int) -> None:  # pragma: no cover - passthrough
        os.close(fh)

    # ----------------------- decoy helpers -----------------------
    def _populate_decoy(self, profile: str) -> None:
        data = _DECOY_PROFILES.get(profile)
        if data is None:
            raise ValueError(f"Unknown decoy profile: {profile}")
        for name, content in data.items():
            p = self.root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)


def mount_fs(
    container: Path, mountpoint: Path, password: str, *, foreground: bool = True, decoy_profile: str | None = None
) -> None:
    """Mount CONTAINER on MOUNTPOINT."""
    if FUSE is None:
        raise RuntimeError("fusepy is not installed")
    mountpoint.mkdir(parents=True, exist_ok=True)
    fs = ZilantFS(container, password.encode(), decoy_profile=decoy_profile)
    FUSE(fs, str(mountpoint), foreground=foreground)


def umount_fs(mountpoint: Path) -> None:
    """Unmount MOUNTPOINT."""
    if os.name == "nt":
        subprocess.run(["fsutil", "volume", "dismount", str(mountpoint)], check=True)
    else:
        subprocess.run(["fusermount", "-u", str(mountpoint)], check=True)
