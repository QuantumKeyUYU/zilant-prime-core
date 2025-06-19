from click.testing import CliRunner
from pathlib import Path

from zilant_prime_core.cli import cli

KEY = b"K" * 16


def test_cli_shard_roundtrip(tmp_path: Path) -> None:
    key_file = tmp_path / "master.key"
    key_file.write_bytes(KEY)
    shares_dir = tmp_path / "shares"
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "key",
            "shard",
            "export",
            "--threshold",
            "2",
            "--shares",
            "3",
            "--output-dir",
            str(shares_dir),
            "--in-key",
            str(key_file),
        ],
    )
    assert result.exit_code == 0, result.output
    files = sorted(shares_dir.glob("share_*.bin"))
    assert len(files) == 3
    files[0].write_bytes(b"x" + files[0].read_bytes()[1:])
    files[0].unlink()  # drop corrupted share
    out_file = tmp_path / "recovered.bin"
    result = runner.invoke(
        cli,
        [
            "key",
            "shard",
            "import",
            "--inputs",
            str(shares_dir),
            "--output",
            str(out_file),
        ],
    )
    assert result.exit_code == 0, result.output
    assert out_file.read_bytes() == KEY


def test_cli_shard_stdin_stdout(tmp_path: Path) -> None:
    shares_dir = tmp_path / "shares"
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "key",
            "shard",
            "export",
            "--threshold",
            "2",
            "--shares",
            "2",
            "--output-dir",
            str(shares_dir),
        ],
        input=KEY,
    )
    assert result.exit_code == 0
    result = runner.invoke(
        cli,
        [
            "key",
            "shard",
            "import",
            "--inputs",
            str(shares_dir),
        ],
    )
    assert result.exit_code == 0
    assert result.stdout.encode() == KEY


def test_cli_shard_invalid(tmp_path: Path) -> None:
    key_file = tmp_path / "m.key"
    key_file.write_bytes(KEY)
    result = CliRunner().invoke(
        cli,
        [
            "key",
            "shard",
            "export",
            "--threshold",
            "5",
            "--shares",
            "3",
            "--output-dir",
            str(tmp_path / "d"),
            "--in-key",
            str(key_file),
        ],
    )
    assert result.exit_code != 0
