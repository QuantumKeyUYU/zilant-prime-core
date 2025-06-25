from __future__ import annotations

import errno
import hashlib
import json
import os
import subprocess
import tarfile
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Dict, cast

from .utils import fs as _fs_patch  # noqa: F401  # ensure mkfifo/sync stubs on Windows

try:  # pragma: no cover - optional dependency may be missing
    from fuse import FUSE, FuseOSError, Operations  # type: ignore
except Exception:  # pragma: no cover - optional dependency may be missing
    FUSE = None  # type: ignore[assignment]
    FuseOSError = OSError  # type: ignore[misc]

    class _Operations:
        pass

    Operations = _Operations

try:
    from zilant_prime_core.container import get_metadata, pack_file, unpack_file
except ModuleNotFoundError:  # pragma: no cover - dev
    from container import get_metadata, pack_file, unpack_file
try:
    from zilant_prime_core.streaming_aead import pack_stream, unpack_stream
except ModuleNotFoundError:  # pragma: no cover - dev
    from streaming_aead import pack_stream, unpack_stream
from zilant_prime_core.utils.logging import get_logger

from logging import Logger

logger = cast(Logger, get_logger("zilfs"))

_DECOY_PROFILES: Dict[str, Dict[str, str]] = {"minimal": {"dummy.txt": "lorem ipsum", "pics/kitten.jpg": "PLACEHOLDER"}}

ACTIVE_FS: list["ZilantFS"] = []


def pack_dir(src: Path, dest: Path, key: bytes) -> None:
    """Pack directory *src* into encrypted container *dest*."""
    with TemporaryDirectory() as tmp:
        tar_path = Path(tmp) / "data.tar"
        with tarfile.open(tar_path, "w") as tar:
            tar.add(src, arcname=".")
        pack_file(tar_path, dest, key)


def pack_dir_stream(src: Path, dest: Path, key: bytes) -> None:
    """Pack directory using a streaming TAR writer."""
    with TemporaryDirectory() as tmp:
        fifo = Path(tmp) / "pipe"
        try:
            os.mkfifo(fifo)
        except (AttributeError, NotImplementedError, OSError):
            pack_dir(src, dest, key)
            return
        proc = subprocess.Popen(["tar", "-C", str(src), "-cf", str(fifo), "."])
        pack_stream(fifo, dest, key)
        proc.wait()


def unpack_dir(container: Path, dest: Path, key: bytes) -> None:
    """Unpack encrypted container *container* into directory *dest*."""
    with open(container, "rb") as fh:
        header = bytearray()
        while not header.endswith(b"\n\n") and len(header) < 1024:
            b = fh.read(1)
            if not b:
                break
            header.extend(b)
        try:
            meta = json.loads(header[:-2].decode("utf-8"))
        except Exception:
            meta = {}
    if meta.get("magic") == "ZSTR":
        with TemporaryDirectory() as tmp:
            tar_path = Path(tmp) / "data.tar"
            unpack_stream(container, tar_path, key)
            with tarfile.open(tar_path, "r") as tar:
                tar.extractall(dest)  # nosec
    else:
        with TemporaryDirectory() as tmp:
            tar_path = Path(tmp) / "data.tar"
            unpack_file(container, tar_path, key)
            with tarfile.open(tar_path, "r") as tar:
                tar.extractall(dest)  # nosec


def _rewrite_metadata(container: Path, extra: dict[str, Any], key: bytes) -> None:
    """Rewrite header of *container* with updated ``extra`` metadata."""
    with TemporaryDirectory() as tmp:
        plain = Path(tmp) / "plain"
        unpack_file(container, plain, key)
        pack_file(plain, container, key, extra_meta=extra)


def snapshot_container(container: Path, key: bytes, label: str) -> Path:
    """Create a new snapshot of CONTAINER labeled LABEL."""
    base_meta = get_metadata(container)
    snapshots = cast(Dict[str, str], base_meta.get("snapshots", {}))
    with TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        unpack_dir(container, tmp_dir, key)
        out = container.with_name(f"{container.stem}_{label}{container.suffix}")
        extra = {
            "label": label,
            "latest_snapshot_id": label,
            "snapshots": {**snapshots, label: str(int(time.time()))},
        }
        pack_dir(tmp_dir, out, key)
        _rewrite_metadata(out, extra, key)

    # update base container anti-rollback token
    update = {
        "latest_snapshot_id": label,
        "snapshots": {**snapshots, label: str(int(time.time()))},
    }
    _rewrite_metadata(container, update, key)
    return out


def diff_snapshots(path_a: Path, path_b: Path, key: bytes) -> dict[str, tuple[str, str]]:
    """Return hash differences between two snapshot containers."""

    def _hash_tree(base: Path) -> dict[str, str]:
        res: dict[str, str] = {}
        for p in sorted(base.rglob("*")):
            if p.is_file():
                res[str(p.relative_to(base))] = hashlib.sha256(p.read_bytes()).hexdigest()
        return res

    with TemporaryDirectory() as tmp1, TemporaryDirectory() as tmp2:
        d1 = Path(tmp1)
        d2 = Path(tmp2)
        unpack_dir(path_a, d1, key)
        unpack_dir(path_b, d2, key)
        h1 = _hash_tree(d1)
        h2 = _hash_tree(d2)

    out: dict[str, tuple[str, str]] = {}
    for name in sorted(set(h1) | set(h2)):
        if h1.get(name) != h2.get(name):
            out[name] = (h1.get(name, ""), h2.get(name, ""))
    return out


class ZilantFS(Operations):
    """Simple FUSE filesystem exposing a directory tree."""

    def __init__(
        self, container: Path, password: bytes, *, decoy_profile: str | None = None, force: bool = False
    ) -> None:
        self.container = Path(container)
        self.password = password
        self.ro = False
        self._bytes_rw = 0
        self._start = time.time()
        self._tmp = TemporaryDirectory()
        self.root = Path(self._tmp.name)
        meta = get_metadata(self.container) if self.container.exists() else {}
        if not force and meta.get("latest_snapshot_id") and meta.get("label") != meta["latest_snapshot_id"]:
            raise RuntimeError("rollback detected: mount with --force")

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
        ACTIVE_FS.append(self)

    # ------------------------- helpers -------------------------
    def _full_path(self, path: str) -> str:
        return str(self.root / path.lstrip("/"))

    def _check_rw(self) -> None:
        if self.ro:
            raise FuseOSError(errno.EACCES)

    def throughput_mb_s(self) -> float:
        """Return throughput since last call in MB/s."""
        dur = max(time.time() - self._start, 0.001)
        mb = self._bytes_rw / (1024 * 1024)
        self._bytes_rw = 0
        self._start = time.time()
        return mb / dur

    # ------------------------- FUSE API -------------------------
    def destroy(self, path: str) -> None:  # pragma: no cover - called on unmount
        if not self.ro:
            if os.environ.get("ZILANT_STREAM", "0") != "0":
                pack_dir_stream(self.root, self.container, self.password)
            else:
                pack_dir(self.root, self.container, self.password)
        if os.environ.get("ZILANT_SHRED") == "1":
            for p in self.root.rglob("*"):
                if p.is_file():
                    try:
                        if os.name == "nt":
                            subprocess.run(["sdelete", "-q", str(p)], check=True)
                        else:
                            subprocess.run(["shred", "-uz", str(p)], check=True)
                    except Exception as exc:  # pragma: no cover - best effort
                        logger.warning("shred_failed:%s", exc)
        self._tmp.cleanup()
        if self in ACTIVE_FS:
            ACTIVE_FS.remove(self)

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
        data = os.read(fh, size)
        self._bytes_rw += len(data)
        return data

    def write(self, path: str, data: bytes, offset: int, fh: int) -> int:
        self._check_rw()
        os.lseek(fh, offset, os.SEEK_SET)
        n = os.write(fh, data)
        self._bytes_rw += n
        return n

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
        if profile == "adaptive":
            from .decoy_gen import generate

            data = {name: "" for name in generate().keys()}
        else:
            data = _DECOY_PROFILES.get(profile) or {}
            if not data:
                raise ValueError(f"Unknown decoy profile: {profile}")
        for name, content in data.items():
            p = self.root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)


def mount_fs(
    container: Path,
    mountpoint: Path,
    password: str,
    *,
    foreground: bool = True,
    decoy_profile: str | None = None,
    remote: str | None = None,
    force: bool = False,
) -> None:
    """Mount CONTAINER on MOUNTPOINT."""
    if FUSE is None:
        raise RuntimeError("fusepy is not installed")
    mountpoint.mkdir(parents=True, exist_ok=True)
    remote_mp: Path | None = None
    if remote:
        remote_mp = mountpoint / ".remote"
        remote_mp.mkdir(exist_ok=True)
        subprocess.run(["sshfs", remote, str(remote_mp)], check=True)
        container = remote_mp / Path(remote).name
    fs = ZilantFS(container, password.encode(), decoy_profile=decoy_profile, force=force)
    FUSE(fs, str(mountpoint), foreground=foreground)
    if remote_mp:
        umount_fs(remote_mp)


def umount_fs(mountpoint: Path) -> None:
    """Unmount MOUNTPOINT."""
    if os.name == "nt":
        subprocess.run(["fsutil", "volume", "dismount", str(mountpoint)], check=True)
    else:
        subprocess.run(["fusermount", "-u", str(mountpoint)], check=True)
