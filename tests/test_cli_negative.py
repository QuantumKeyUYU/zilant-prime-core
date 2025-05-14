import os
from click.testing import CliRunner
from zilant_prime_core.cli import cli


def test_cli_wrong_password(tmp_path):
    runner = CliRunner(mix_stderr=False)
    src = tmp_path / "file.txt"
    src.write_text("x")
    result = runner.invoke(cli, ["pack", str(src), "-p", "-"], input="pw1\npw2\n")
    assert result.exit_code == 1
    assert "Passwords do not match" in result.output


def test_cli_overwrite(tmp_path):
    runner = CliRunner(mix_stderr=False)
    src = tmp_path / "a.bin"
    src.write_bytes(os.urandom(4))
    # pack
    runner.invoke(cli, ["pack", str(src), "-p", "x"])
    # unpack
    container = src.with_suffix(".zil")
    out_dir = tmp_path / "out"
    runner.invoke(cli, ["unpack", str(container), "-p", "x", "-d", str(out_dir)])
    # second attempt without --overwrite -> should fail (exit 1)
    result = runner.invoke(cli, ["unpack", str(container), "-p", "x", "-d", str(out_dir)])
    assert result.exit_code == 1
