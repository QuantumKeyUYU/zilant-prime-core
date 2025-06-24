import hashlib
import os
import pytest
import subprocess
import time

pytestmark = pytest.mark.wormhole

MSG = b"hello-wormhole\n" * 1024


def _sha(b: bytes):
    return hashlib.sha256(b).hexdigest()


def test_wormhole_roundtrip(tmp_path):
    if "WORM_PORT" not in os.environ:
        pytest.skip("no relay")
    if os.environ.get("GITHUB_REF") != "refs/heads/main":
        pytest.skip("only on main")
    fn = tmp_path / "in.bin"
    fn.write_bytes(MSG)
    port = os.environ["WORM_PORT"]
    code = "root"

    snd = subprocess.Popen(
        ["zilctl", "wormhole", "send", str(fn), "--relay", f"ws://localhost:{port}"],
        stdin=subprocess.PIPE,
        text=True,
    )
    time.sleep(1)
    rcv = subprocess.Popen(
        ["zilctl", "wormhole", "receive", "--code", code, "--relay", f"ws://localhost:{port}"],
        cwd=tmp_path,
    )
    snd.communicate(input=f"{code}\n", timeout=15)
    assert snd.wait() == 0 and rcv.wait(timeout=15) == 0
    out = tmp_path / "in.bin"
    assert _sha(MSG) == _sha(out.read_bytes())
