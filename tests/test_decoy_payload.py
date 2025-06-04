from click.testing import CliRunner
from zilant_prime_core.cli import cli
from pathlib import Path


def test_pack_with_decoy_size(tmp_path: Path):
    src = tmp_path / "foo.txt"
    src.write_bytes(b"ABCD")
    runner = CliRunner()
    result = runner.invoke(cli, ["pack", str(src), "-p", "pwd", "--decoy-size", "10"])
    assert result.exit_code == 0
    out = tmp_path / "foo.zil"
    assert out.exists()
    content = out.read_bytes().split(b"\n", 1)[1]
    assert len(content) == 10
    assert content.startswith(b"ABCD")
    assert content.endswith(b"\x00" * 6)


def test_pack_with_decoy_size_too_small(tmp_path: Path):
    src = tmp_path / "foo.txt"
    src.write_bytes(b"ABCDEFGHIJK")
    runner = CliRunner()
    result = runner.invoke(cli, ["pack", str(src), "-p", "pwd", "--decoy-size", "10"])
    assert result.exit_code != 0
    assert "Payload too large" in result.output
