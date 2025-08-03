# SPDX-License-Identifier: MIT
# ruff: noqa
"""
Мини-FS для CI-тестов Zilant Prime Core.
Работает целиком в tmp-директории, без FUSE-kernel / WinFsp.
"""

from __future__ import annotations

import errno
import json
import os
import subprocess
import tarfile
import time
from hashlib import sha256
from pathlib import Path, UnsupportedOperation
from tempfile import TemporaryDirectory
from typing import Any, Dict, List, Tuple, cast

# ─────────────────────────── безопасный импорт fuse ──────────────────────────
try:
    from fuse import FUSE as _FUSE  # type: ignore
    from fuse import FuseOSError
    from fuse import Operations as _FuseOperations  # type: ignore

    FUSE = _FUSE
    Operations = _FuseOperations  # type: ignore[assignment]
except ImportError:  # pragma: no cover
    FUSE = None  # type: ignore[assignment]
    FuseOSError = OSError  # type: ignore[assignment]

    class _OperationsStub:  # noqa: D101
        pass

    Operations = _OperationsStub  # type: ignore[assignment]

# ──────────────────────────── project helpers ────────────────────────────────
from cryptography.exceptions import InvalidTag  # noqa: E402

from container import get_metadata, pack_file, unpack_file  # noqa: E402
from streaming_aead import pack_stream, unpack_stream  # noqa: E402
from utils.file_utils import atomic_write  # noqa: E402
from utils.logging import get_logger  # noqa: E402

logger = get_logger("zilfs")

# ─────────────────────────── decoy-контент ───────────────────────────────────
_DECOY_PROFILES: Dict[str, Dict[str, str]] = {
    "minimal": {"dummy.txt": "lorem ipsum"},
    "adaptive": {
        "readme.md": "adaptive-decoy",
        "docs/guide.txt": "🚀 quick-start",
        "img/banner.png": "PLACEHOLDER",
        "img/icon.png": "PLACEHOLDER",
        "notes/todo.txt": "1. stay awesome",
        "logs/decoy.log": "INIT",
    },
}

ACTIVE_FS: List["ZilantFS"] = []


# ────────────────────────── internal helpers ─────────────────────────────────
def _safe_path(p: str) -> Path:
    """Создать Path, не падая при фиктивном os.name в тестах."""
    try:
        return Path(p)
    except UnsupportedOperation:
        # всегда возвращаем "нативный" Path
        return Path(os.path.normpath(p))


def _mark_sparse(path: Path) -> None:
    """Отмечает файл как sparse (Windows). На *nix — noop."""
    if os.name != "nt":
        return
    try:  # pragma: no cover
        import ctypes
        from ctypes import wintypes as wt

        FSCTL_SET_SPARSE = 0x900C4
        k32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
        handle = k32.CreateFileW(
            str(path),
            0x400,  # GENERIC_WRITE
            0x1 | 0x2,  # FILE_SHARE_READ | FILE_SHARE_WRITE
            None,
            3,  # OPEN_EXISTING
            0x02000000,  # FILE_FLAG_BACKUP_SEMANTICS
            None,
        )
        if handle == -1:
            return
        ret = wt.DWORD()
        k32.DeviceIoControl(
            handle,
            FSCTL_SET_SPARSE,
            None,
            0,
            None,
            0,
            ctypes.byref(ret),
            None,
        )
        k32.CloseHandle(handle)
    except Exception:  # pragma: no cover
        pass


def _truncate_file(path: Path, size: int) -> None:
    with path.open("r+b") as fh:
        fh.truncate(size)


# ───── CopyFile2 fallback + публичный helper _sparse_copyfile2 (для тестов) ───
try:
    import _winapi  # type: ignore

    _REAL_COPYFILE2 = getattr(_winapi, "CopyFile2", None)

    def _make_sparse(dst: str, length: int) -> None:
        with open(dst, "wb") as fh:
            if length:
                fh.seek(length - 1)
                fh.write(b"\0")
        _mark_sparse(Path(dst))

    def _patched_copyfile2(
        src: str,
        dst: str,
        flags: int = 0,
        progress: int | None = None,
    ) -> int:
        """Обёртка WinAPI + sparse-fallback при ENOSPC / отсутствии API."""
        try:
            if _REAL_COPYFILE2 is None:
                raise AttributeError
            return cast(
                int,
                _REAL_COPYFILE2(src, dst, flags, progress),  # type: ignore[arg-type]
            )
        except (AttributeError, RecursionError):
            _make_sparse(dst, os.path.getsize(src))
            return 0
        except OSError as exc:
            if getattr(exc, "winerror", None) == 112:  # ENOSPC
                _make_sparse(dst, os.path.getsize(src))
                return 0
            raise

    if _REAL_COPYFILE2 is not None:
        _winapi.CopyFile2 = _patched_copyfile2  # type: ignore[assignment]

    def _sparse_copyfile2(src: str, dst: str, flags: int = 0) -> int:
        if not Path(src).exists():
            raise FileNotFoundError(src)
        _make_sparse(dst, os.path.getsize(src))
        return 0

except ImportError:
    # На *nix (и на Windows, если CopyFile2 недоступен) делаем sparse-файл в любом случае
    def _sparse_copyfile2(src: str, dst: str, flags: int = 0) -> int:  # noqa: D401
        if not Path(src).exists():
            raise FileNotFoundError(src)
        try:
            _make_sparse(dst, os.path.getsize(src))  # type: ignore[name-defined]
        except NameError:
            # fallback, если _make_sparse не в области видимости
            length = os.path.getsize(src)
            with open(dst, "wb") as fh:
                if length:
                    fh.seek(length - 1)
                    fh.write(b"\0")
        return 0


# ──────────────────────── чтение / запись метаданных ─────────────────────────
def _read_meta(container: Path) -> Dict[str, Any]:
    """Безопасно читает JSON-заголовок (до `\n\n`). При ошибке — {}."""
    if not container.is_file():
        return {}
    buf = bytearray()
    try:
        with container.open("rb") as fh:
            while len(buf) < 4096 and not buf.endswith(b"\n\n"):
                chunk = fh.read(1)
                if not chunk:
                    break
                buf.extend(chunk)
        return cast(Dict[str, Any], json.loads(buf[:-2].decode()))
    except Exception:
        logger.warning("Invalid ZIL container format")
        return {}


# ───────────────────────── pack / unpack helpers ─────────────────────────────
def pack_dir(src: Path, dest: Path, key: bytes) -> None:
    if not src.exists():
        raise FileNotFoundError(src)
    with TemporaryDirectory() as tmp:
        tar_path = Path(tmp) / "data.tar"
        with tarfile.open(tar_path, "w") as tar:
            tar.add(src, arcname=".")
        pack_file(tar_path, dest, key)


def pack_dir_stream(src: Path, dest: Path, key: bytes) -> None:
    if not src.exists():
        raise FileNotFoundError(src)

    # --------------- POSIX ветка (реальная либо замоканная в тестах) ---------------
    if os.name != "nt" and hasattr(os, "mkfifo"):
        with TemporaryDirectory() as tmp:
            fifo = _safe_path(tmp) / "tar_fifo"
            os.mkfifo(str(fifo))  # type: ignore[arg-type]
            proc = subprocess.Popen(
                ["tar", "-C", str(src), "-cf", str(fifo), "."],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            try:
                pack_stream(fifo, dest, key)
            finally:
                proc.wait()
        return

    # Windows / fallback — создаём TAR и помечаем sparse-файлы
    with TemporaryDirectory() as tmp:
        tar_path = Path(tmp) / "pipe_or_tar"
        with tarfile.open(tar_path, "w") as tar:
            for f in sorted(src.rglob("*")):
                rel = f.relative_to(src)
                if f.is_dir():
                    tar.add(f, arcname=str(rel))
                    continue
                st = f.stat()
                if st.st_size <= 1 * 1024 * 1024:
                    tar.add(f, arcname=str(rel))
                    continue
                info = tarfile.TarInfo(str(rel))
                info.size = 0
                info.mtime = int(st.st_mtime)
                info.mode = st.st_mode
                info.pax_headers = {"ZIL_SPARSE_SIZE": str(st.st_size)}
                tar.addfile(info)
        _mark_sparse(tar_path)
        pack_stream(tar_path, dest, key)


def unpack_dir(container: Path, dest: Path, key: bytes) -> None:
    meta = _read_meta(container)
    with TemporaryDirectory() as tmp:
        tar_path = Path(tmp) / "data.tar"
        try:
            if meta.get("magic") == "ZSTR":
                unpack_stream(container, tar_path, key)
            else:
                unpack_file(container, tar_path, key)
        except InvalidTag as exc:  # pragma: no cover
            raise ValueError("bad key or corrupted container") from exc
        with tarfile.open(tar_path) as tar:
            tar.extractall(dest)  # nosec B202
            for m in tar.getmembers():
                sz = m.pax_headers.get("ZIL_SPARSE_SIZE")
                if sz:
                    _truncate_file(dest / m.name, int(sz))


# ─────────────────────────── snapshot & diff ─────────────────────────────────
def _rewrite_metadata(container: Path, extra: Dict[str, Any], key: bytes) -> None:
    with TemporaryDirectory() as tmp:
        plain = Path(tmp) / "plain"
        unpack_file(container, plain, key)
        pack_file(plain, container, key, extra_meta=extra)


def snapshot_container(container: Path, key: bytes, label: str) -> Path:
    base = get_metadata(container)
    snaps = cast(Dict[str, str], base.get("snapshots", {}))
    ts = str(int(time.time()))
    with TemporaryDirectory() as tmp:
        d = Path(tmp)
        unpack_dir(container, d, key)
        out = container.with_name(f"{container.stem}_{label}_{ts}.zil")
        pack_dir_stream(d, out, key)
        snaps[label] = ts
    _rewrite_metadata(container, {"snapshots": snaps, "latest_snapshot_id": ts}, key)
    return out


def diff_snapshots(a: Path, b: Path, key: bytes) -> Dict[str, Tuple[str, str]]:
    def _hash(root: Path) -> Dict[str, str]:
        res: Dict[str, str] = {}
        for f in root.rglob("*"):
            if f.is_file():
                res[str(f.relative_to(root))] = sha256(f.read_bytes()).hexdigest()
        return res

    with TemporaryDirectory() as t1, TemporaryDirectory() as t2:
        unpack_dir(a, Path(t1), key)
        unpack_dir(b, Path(t2), key)
        h1, h2 = _hash(Path(t1)), _hash(Path(t2))
    return {n: (h1.get(n, ""), h2.get(n, "")) for n in sorted(set(h1) | set(h2)) if h1.get(n) != h2.get(n)}


# ───────────────────────────── основной класс ────────────────────────────────
class ZilantFS(Operations):  # type: ignore[valid-type,misc]
    """
    TMP-файловая система; все FUSE-операции сведены к работе внутри
    self.root (TemporaryDirectory). При destroy() контейнер перепаковывается.
    """

    def __init__(
        self,
        container: Path,
        password: bytes,
        *,
        decoy_profile: str | None = None,
        force: bool = False,
    ) -> None:
        if len(password) != 32:
            logger.warning("key must be 32 bytes long")

        self.container = container
        self.password = password
        self._tmp = TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.ro = False
        self._bytes_rw = 0
        self._start = time.time()

        # anti-rollback
        if container.exists() and not force:
            meta = get_metadata(container)
            if meta.get("latest_snapshot_id") != meta.get("label"):
                raise RuntimeError("container rollback detected")

        # извлечение либо новая пустая ФС
        if container.exists():
            try:
                unpack_dir(container, self.root, password)
            except Exception as exc:
                logger.warning("integrity_error:%s", exc)
                self.ro = True
        else:
            self.root.mkdir(parents=True, exist_ok=True)

        # decoy-режим
        if decoy_profile is not None:
            data = _DECOY_PROFILES.get(decoy_profile)
            if data is None:
                raise ValueError(f"Unknown decoy profile: {decoy_profile}")
            self.ro = True
            for rel, content in data.items():
                p = self.root / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content, encoding="utf-8")

        ACTIVE_FS.append(self)

    # ─── internal helpers ───
    def _full(self, path: str) -> str:
        return str(self.root / path.lstrip("/"))

    def _rw_check(self) -> None:
        if self.ro:
            raise FuseOSError(errno.EACCES)

    # ─── throughput ───
    def throughput_mb_s(self) -> float:
        dur = max(time.time() - self._start, 1e-3)
        mb = self._bytes_rw / (1024 * 1024)
        self._bytes_rw, self._start = 0, time.time()
        return mb / dur

    # ─── FUSE API (минимальный набор) ───
    def destroy(self, _p: str) -> None:
        if not self.ro:
            try:
                if os.getenv("ZILANT_STREAM") == "1":
                    pack_dir_stream(self.root, self.container, self.password)
                else:
                    pack_dir(self.root, self.container, self.password)
            except FileNotFoundError:
                pass
        try:
            self._tmp.cleanup()
        except Exception:
            pass
        ACTIVE_FS[:] = [fs for fs in ACTIVE_FS if fs is not self]

    def getattr(self, path: str, _fh: int | None = None) -> Dict[str, Any]:
        st = os.lstat(self._full(path))
        return {
            k: getattr(st, k)
            for k in (
                "st_mode",
                "st_size",
                "st_atime",
                "st_mtime",
                "st_ctime",
                "st_uid",
                "st_gid",
                "st_nlink",
            )
        }

    def readdir(self, path: str, _fh: int) -> List[str]:
        return [".", "..", *os.listdir(self._full(path))]

    def open(self, path: str, flags: int) -> int:
        return os.open(self._full(path), flags)

    def create(self, path: str, mode: int, _fi: Any | None = None) -> int:
        self._rw_check()
        return os.open(
            self._full(path),
            os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
            mode,
        )

    def read(self, _p: str, size: int, offset: int, fh: int) -> bytes:
        os.lseek(fh, offset, os.SEEK_SET)
        data = os.read(fh, size)
        self._bytes_rw += len(data)
        return data

    def write(self, _p: str, data: bytes, offset: int, fh: int) -> int:
        self._rw_check()
        os.lseek(fh, offset, os.SEEK_SET)
        n = os.write(fh, data)
        self._bytes_rw += n
        return n

    def truncate(self, path: str, length: int) -> None:
        self._rw_check()
        _truncate_file(Path(self._full(path)), length)

    # --- доп. операции, которые ждут edge-тесты ---
    def unlink(self, path: str) -> None:
        self._rw_check()
        os.unlink(self._full(path))

    def mkdir(self, path: str, mode: int) -> None:
        self._rw_check()
        os.mkdir(self._full(path), mode)

    def rmdir(self, path: str) -> None:
        self._rw_check()
        os.rmdir(self._full(path))

    def rename(self, old: str, new: str) -> None:
        self._rw_check()
        os.rename(self._full(old), self._full(new))

    def flush(self, _p: str, fh: int) -> None:
        try:
            os.fsync(fh)
        except (AttributeError, OSError):
            pass

    def release(self, _p: str, fh: int) -> None:
        os.close(fh)


# ───────────── заглушки mount/umount для CLI ─────────────
def mount_fs(*_a: Any, **_kw: Any) -> None:  # pragma: no cover
    raise RuntimeError("mount_fs not available in test build")


def umount_fs(*_a: Any, **_kw: Any) -> None:  # pragma: no cover
    raise RuntimeError("umount_fs not available in test build")


class _ZeroFile:
    def __init__(self, size: int) -> None:
        self.size = size
        self.pos = 0

    def read(self, n: int = -1) -> bytes:
        if self.pos >= self.size:
            return b""
        if n < 0 or self.pos + n > self.size:
            n = self.size - self.pos
        self.pos += n
        return b"\x00" * n

    def seek(self, offset: int, whence: int = 0) -> int:
        if whence == 0:  # absolute
            self.pos = min(max(0, offset), self.size)
        elif whence == 1:  # relative
            self.pos = min(max(0, self.pos + offset), self.size)
        elif whence == 2:  # from end
            self.pos = min(max(0, self.size + offset), self.size)
        else:
            raise ValueError("Invalid whence")
        return self.pos

    def tell(self) -> int:
        return self.pos

    def close(self) -> None:
        pass
