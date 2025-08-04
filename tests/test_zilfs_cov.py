import os
import pytest
import subprocess
import sys

import zilant_prime_core.zilfs as zfs
from zilant_prime_core.zilfs import _truncate_file, _ZeroFile, pack_dir, unpack_dir


@pytest.mark.skipif(not hasattr(zfs, "_ORIG_COPYFILE2"), reason="Windows-only CopyFile2 fallback")
def test_sparse_copyfile2_winerror(monkeypatch, tmp_path):
    src = tmp_path / "big.bin"
    src.write_bytes(b"ABC")
    dst = tmp_path / "dst.bin"

    def fake_copy(src_, dst_, flags, progress=None):
        err = OSError("no space")
        err.winerror = 112
        raise err

    monkeypatch.setenv("ZILANT_STREAM", "0")
    monkeypatch.setattr(zfs, "_ORIG_COPYFILE2", fake_copy, raising=False)
    zfs._patched_copyfile2(str(src), str(dst), 0)
    assert dst.exists()
    assert dst.stat().st_size == 3
    assert dst.read_bytes() == b"\0" * 3


@pytest.mark.skipif(sys.platform.startswith("win"), reason="PosixPath нельзя инстанцировать на Windows")
def test_pack_dir_stream_fifo(tmp_path, monkeypatch):
    src = tmp_path / "src"
    src.mkdir()
    (src / "foo.txt").write_text("hello")
    out = tmp_path / "out.zil"
    key = b"x" * 32
    monkeypatch.setenv("ZILANT_STREAM", "1")
    monkeypatch.setattr(os, "name", "posix", raising=False)
    monkeypatch.setattr(os, "mkfifo", lambda path: None, raising=False)

    class FakeProc:
        def __init__(*a, **k):
            pass

        def wait(self):
            pass

    monkeypatch.setattr(subprocess, "Popen", lambda *a, **k: FakeProc(), raising=False)
    monkeypatch.setattr(
        zfs,
        "pack_stream",
        lambda fifo, dest, key: dest.write_bytes(b"X"),
        raising=False,
    )
    zfs.pack_dir_stream(src, out, key)
    assert out.is_file()
    assert out.read_bytes() == b"X"


def test_snapshot_and_diff(tmp_path):
    d = tmp_path / "d"
    d.mkdir()
    (d / "x.txt").write_text("one")
    key = b"p" * 32
    base = tmp_path / "base.zil"
    pack_dir(d, base, key)
    snap1 = zfs.snapshot_container(base, key, "v1")
    unpack_dir(base, d, key)
    (d / "x.txt").write_text("two")
    pack_dir(d, base, key)
    snap2 = zfs.snapshot_container(base, key, "v2")
    diff = zfs.diff_snapshots(snap1, snap2, key)
    assert "x.txt" in diff
    assert diff["x.txt"][0] != diff["x.txt"][1]


def test_stub_mount_api():
    for fn in (zfs.mount_fs, zfs.umount_fs):
        with pytest.raises(RuntimeError):
            fn()


def test_throughput(tmp_path):
    fs = zfs.ZilantFS(tmp_path / "c.zil", b"k" * 32, force=True)
    (fs.root / "f.bin").write_bytes(b"\0" * 1024 * 1024)
    fs.destroy("/")
    val = fs.throughput_mb_s()
    assert isinstance(val, float) and val >= 0.0


def test_zerofile_and_truncate(tmp_path):
    z = _ZeroFile(10)
    d1 = z.read(4)
    assert d1 == b"\0" * 4
    d2 = z.read()
    assert d2 == b"\0" * 6
    assert z.read() == b""
    f = tmp_path / "t.bin"
    f.write_bytes(b"ABCDEFGHIJ")
    _truncate_file(f, 3)
    assert f.read_bytes() == b"ABC"
