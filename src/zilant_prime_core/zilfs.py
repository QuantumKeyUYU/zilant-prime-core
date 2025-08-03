# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

from __future__ import annotations
import errno, json, os, subprocess, tarfile, time
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Dict, List, Tuple, cast

class Operations:
    """Заглушка, если fusepy не установлен — нужна только для типизации."""

FUSE: Any | None = None
try:
    from fuse import FUSE as _FUSE, FuseOSError, Operations as _Ops
    FUSE = _FUSE
    Operations = _Ops
except ImportError:
    FuseOSError = OSError

from cryptography.exceptions import InvalidTag
from container import get_metadata, pack_file, unpack_file
from streaming_aead import pack_stream, unpack_stream
from utils.logging import get_logger

logger = get_logger("zilfs")
_DECOY_PROFILES: Dict[str, Dict[str, str]] = {"minimal": {"dummy.txt": "lorem ipsum"}, "adaptive": {"readme.md": "adaptive-decoy", "docs/guide.txt": "🚀 quick-start", "img/banner.png": "PLACEHOLDER", "img/icon.png": "PLACEHOLDER", "notes/todo.txt": "1. stay awesome", "logs/decoy.log": "INIT"}}
ACTIVE_FS: List["ZilantFS"] = []

class _ZeroFile:
    def __init__(self, size: int) -> None:
        self._size = size
        self._pos = 0
    def read(self, n: int = -1) -> bytes:
        if self._pos >= self._size: return b""
        bytes_to_read = self._size - self._pos
        if n != -1 and n < bytes_to_read: bytes_to_read = n
        self._pos += bytes_to_read
        return b"\0" * bytes_to_read
    def seek(self, offset: int, whence: int = 0) -> int:
        if whence == 0: self._pos = offset
        elif whence == 1: self._pos += offset
        elif whence == 2: self._pos = self._size + offset
        else: raise ValueError(f"invalid whence ({whence}, should be 0, 1 or 2)")
        if self._pos < 0: self._pos = 0
        return self._pos
    def tell(self) -> int: return self._pos
    def close(self) -> None: pass

def _mark_sparse(path: Path) -> None:
    if os.name != "nt": return
    try:
        import ctypes
        from ctypes import wintypes as wt
        FSCTL_SET_SPARSE, GENERIC_WRITE, OPEN_EXISTING = 0x900C4, 0x400, 3
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.CreateFileW(str(path), GENERIC_WRITE, 0, None, OPEN_EXISTING, 0x02000000, None)
        if handle == -1: return
        bytes_ret = wt.DWORD()
        kernel32.DeviceIoControl(handle, FSCTL_SET_SPARSE, None, 0, None, 0, ctypes.byref(bytes_ret), None)
        kernel32.CloseHandle(handle)
    except Exception: pass

def _truncate_file(path: Path, size: int) -> None:
    with path.open("r+b") as fh: fh.truncate(size)

def _sparse_copyfile2(src: str, dst: str, _flags: int) -> None:
    length = os.path.getsize(src)
    with open(dst, "wb") as fh:
        if length:
            fh.seek(length - 1)
            fh.write(b"\0")
    _mark_sparse(Path(dst))

try:
    import _winapi as _winapi_mod
    if hasattr(_winapi_mod, "CopyFile2"):
        _ORIG_COPYFILE2 = _winapi_mod.CopyFile2
        def _patched_copyfile2(src: str, dst: str, flags: int = 0, progress: int | None = None) -> int:
            try: return cast(int, _ORIG_COPYFILE2(src, dst, flags, progress))
            except OSError as exc:
                if getattr(exc, "winerror", None) != 112: raise
                _sparse_copyfile2(src, dst, flags)
                return 0
        _winapi_mod.CopyFile2 = _patched_copyfile2
except ImportError: pass

def _read_meta(container: Path) -> Dict[str, Any]:
    header = bytearray()
    with container.open("rb") as fh:
        while not header.endswith(b"\n\n") and len(header) < 4096:
            chunk = fh.read(1)
            if not chunk: break
            header.extend(chunk)
    try: return cast(Dict[str, Any], json.loads(header[:-2].decode()))
    except Exception: return {}

def pack_dir(src: Path, dest: Path, key: bytes) -> None:
    if not src.exists(): raise FileNotFoundError(src)
    with TemporaryDirectory() as tmp:
        tar_path = Path(tmp) / "data.tar"
        with tarfile.open(tar_path, "w") as tar: tar.add(src, arcname=".")
        pack_file(tar_path, dest, key)

def pack_dir_stream(src: Path, dest: Path, key: bytes) -> None:
    with TemporaryDirectory() as tmp:
        fifo = os.path.join(tmp, "pipe_or_tar")
        if os.name != "nt" and hasattr(os, "mkfifo"):
            os.mkfifo(fifo)
            proc = subprocess.Popen(["tar", "-C", str(src), "-cf", fifo, "."], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            pack_stream(Path(fifo), dest, key)
            proc.wait()
            return
        with tarfile.open(fifo, "w") as tar:
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
                info.size, info.mtime, info.mode = 0, int(st.st_mtime), st.st_mode
                info.pax_headers = {"ZIL_SPARSE_SIZE": str(st.st_size)}
                tar.addfile(info, fileobj=_ZeroFile(0))
        _mark_sparse(Path(fifo))
        pack_stream(Path(fifo), dest, key)

def unpack_dir(container: Path, dest: Path, key: bytes) -> None:
    if not container.is_file(): raise FileNotFoundError(container)
    meta = _read_meta(container)
    with TemporaryDirectory() as tmp:
        tar_path = Path(tmp) / "data.tar"
        try:
            if meta.get("magic") == "ZSTR": unpack_stream(container, tar_path, key)
            else: unpack_file(container, tar_path, key)
        except InvalidTag as exc: raise ValueError("bad key or corrupted container") from exc
        with tarfile.open(tar_path) as tar:
            dest_abs = os.path.abspath(dest)
            for member in tar.getmembers():
                member_path = os.path.join(dest_abs, member.name)
                abs_path = os.path.abspath(member_path)
                if not abs_path.startswith(dest_abs): raise ValueError(f"Attempted Path Traversal in TAR file: {member.name}")
            tar.extractall(path=dest)
            for member in tar.getmembers():
                sp_size_str = member.pax_headers.get("ZIL_SPARSE_SIZE")
                if sp_size_str: _truncate_file(dest / member.name, int(sp_size_str))

def _rewrite_metadata(container: Path, extra: Dict[str, Any], key: bytes) -> None:
    with TemporaryDirectory() as tmp:
        plain = Path(tmp) / "plain"
        unpack_file(container, plain, key)
        pack_file(plain, container, key, extra_meta=extra)

def snapshot_container(container: Path, key: bytes, label: str) -> Path:
    if not container.is_file(): raise FileNotFoundError(container)
    base = get_metadata(container)
    snaps = cast(Dict[str, str], base.get("snapshots", {}))
    ts = str(int(time.time()))
    with TemporaryDirectory() as tmp:
        d = Path(tmp)
        unpack_dir(container, d, key)
        out = container.with_name(f"{container.stem}_{label}{container.suffix}")
        pack_dir(d, out, key)
        _rewrite_metadata(out, {"label": label, "latest_snapshot_id": label, "snapshots": {**snaps, label: ts}}, key)
    _rewrite_metadata(container, {"latest_snapshot_id": label, "snapshots": {**snaps, label: ts}}, key)
    return out

def diff_snapshots(a: Path, b: Path, key: bytes) -> Dict[str, Tuple[str, str]]:
    def _hash_tree(root: Path) -> Dict[str, str]:
        r: Dict[str, str] = {}
        for f in sorted(root.rglob("*")):
            if f.is_file(): r[str(f.relative_to(root))] = sha256(f.read_bytes()).hexdigest()
        return r
    with TemporaryDirectory() as t1, TemporaryDirectory() as t2:
        d1, d2 = Path(t1), Path(t2)
        unpack_dir(a, d1, key)
        unpack_dir(b, d2, key)
        h1, h2 = _hash_tree(d1), _hash_tree(d2)
    return {name: (h1.get(name, ""), h2.get(name, "")) for name in sorted(set(h1) | set(h2)) if h1.get(name) != h2.get(name)}

class ZilantFS(Operations):
    def __init__(self, container: Path, password: bytes, *, decoy_profile: str | None = None, force: bool = False) -> None:
        self.container, self.password, self.ro = container, password, False
        self._bytes_rw, self._start, self._tmp = 0, time.time(), TemporaryDirectory()
        self.root = Path(self._tmp.name)
        meta = get_metadata(container) if container.exists() else {}
        if not force and meta.get("latest_snapshot_id") and meta.get("label") != meta["latest_snapshot_id"]: raise RuntimeError("rollback detected: mount with --force")
        if decoy_profile:
            data = _DECOY_PROFILES.get(decoy_profile)
            if data is None: raise ValueError(f"Unknown decoy profile: {decoy_profile}")
            self.ro = True
            for rel, content in data.items():
                p = self.root / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content, encoding="utf-8")
        elif container.exists():
            try: unpack_dir(container, self.root, password)
            except Exception as exc:
                logger.warning("integrity_error:%s", exc)
                self.ro = True
        else: self.root.mkdir(parents=True, exist_ok=True)
        ACTIVE_FS.append(self)

    def _full(self, path: str) -> str: return str(self.root / path.lstrip("/"))
    def _rw_check(self) -> None:
        if self.ro: raise FuseOSError(errno.EACCES)
    def throughput_mb_s(self) -> float:
        dur = max(time.time() - self._start, 1e-3)
        mb = self._bytes_rw / (1024 * 1024)
        self._bytes_rw, self._start = 0, time.time()
        return mb / dur
    def destroy(self, _p: str) -> None:
        if not self.ro:
            try:
                if os.getenv("ZILANT_STREAM") == "1": pack_dir_stream(self.root, self.container, self.password)
                else: pack_dir(self.root, self.container, self.password)
            except FileNotFoundError: pass
        try: self._tmp.cleanup()
        except Exception: pass
        try: ACTIVE_FS.remove(self)
        except ValueError: pass
    def getattr(self, path: str, _fh: int | None = None) -> Dict[str, Any]:
        st = os.lstat(self._full(path))
        keys = ("st_mode", "st_size", "st_atime", "st_mtime", "st_ctime", "st_uid", "st_gid", "st_nlink")
        return {k: getattr(st, k) for k in keys}
    def readdir(self, path: str, _fh: int) -> List[str]: return [".", "..", *os.listdir(self._full(path))]
    def open(self, path: str, flags: int) -> int: return os.open(self._full(path), flags)
    def create(self, path: str, mode: int, _fi: Any | None = None) -> int:
        self._rw_check()
        return os.open(self._full(path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, mode)
    def read(self, _p: str, size: int, offset: int, fh: int) -> bytes:
        os.lseek(fh, offset, os.SEEK_SET)
        data = os.read(fh, size)
        self._bytes_rw += len(data)
        return data
    def write(self, _p: str, data: bytes, offset: int, fh: int) -> int:
        self._rw_check()
        os.lseek(fh, offset, os.SEEK_SET)
        written = os.write(fh, data)
        self._bytes_rw += written
        return written
    def truncate(self, path: str, length: int) -> None:
        self._rw_check()
        _truncate_file(Path(self._full(path)), length)
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
    def flush(self, _p: str, fh: int) -> None: os.fsync(fh)
    def release(self, _p: str, fh: int) -> None: os.close(fh)

def mount_fs(*_a: Any, **_kw: Any) -> None: raise RuntimeError("mount_fs not available in test build")
def umount_fs(*_a: Any, **_kw: Any) -> None: raise RuntimeError("umount_fs not available in test build")