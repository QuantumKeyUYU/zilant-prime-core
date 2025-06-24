import hashlib
import pathlib
import pytest

pytest.importorskip("pexpect")
import pexpect

pytestmark = pytest.mark.wizard


def _sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_wizard_roundtrip(tmp_path: pathlib.Path) -> None:
    tgt = tmp_path / "vault.zil"
    child = pexpect.spawn("zilctl wizard", timeout=20, cwd=tmp_path, encoding="utf-8")
    child.expect("Path to container")
    child.sendline(str(tgt))
    child.expect("New password")
    child.sendline("p@ssw0rd!")
    child.expect("Confirm password")
    child.sendline("p@ssw0rd!")
    child.expect("Generate QR backup")
    child.sendline("y")
    child.expect(r"Mount now\?")
    child.sendline("n")
    child.expect(pexpect.EOF)
    assert tgt.exists() and _sha(tgt) != _sha(pathlib.Path(__file__))
