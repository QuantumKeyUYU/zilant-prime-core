from pathlib import Path

from click.testing import CliRunner

from zilant_prime_core.cli import cli

runner = CliRunner()


def test_pack_no_decoy(tmp_path: Path):
    src = tmp_path / "x.txt"
    src.write_text("hello")
    result = runner.invoke(cli, ["pack", str(src), "-p", "pw"])
    assert result.exit_code == 0, result.output
    arc = src.with_suffix(".zil")
    assert arc.exists()
    assert arc.read_bytes() == b"x.txt\n" + b"hello"


def test_pack_decoy_size(tmp_path: Path):
    src = tmp_path / "a.txt"
    src.write_text("hi")
    dest = tmp_path / "a.zil"
    result = runner.invoke(cli, ["pack", str(src), "-p", "pw", "--decoy-size", "64", "-o", str(dest)])
    assert result.exit_code == 0, result.output
    assert dest.exists()
    assert dest.stat().st_size == 64


def test_pack_decoy_size_too_small(tmp_path: Path):
    src = tmp_path / "b.txt"
    src.write_text("1234567890")
    result = runner.invoke(cli, ["pack", str(src), "-p", "pw", "--decoy-size", "5"])
    assert result.exit_code == 1
    assert "too large" in result.output
