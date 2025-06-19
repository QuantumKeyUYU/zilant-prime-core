from click.testing import CliRunner
from pathlib import Path

from zilant_prime_core.cli import cli

KEY = b"\x01" * 16


def _export(runner: CliRunner, key_file: Path, n: int, t: int, out: Path) -> None:
    args = [
        "key",
        "shard",
        "export",
        "--master-key",
        str(key_file),
        "--n",
        str(n),
        "--t",
        str(t),
        "--out-dir",
        str(out),
    ]
    res = runner.invoke(cli, args)
    assert res.exit_code == 0, res.output


def _import(runner: CliRunner, shares: list[Path], out_file: Path) -> CliRunner:
    args = ["key", "shard", "import", "--out", str(out_file)]
    for s in shares:
        args.extend(["--shares", str(s)])
    return runner.invoke(cli, args)


def test_roundtrip_corrupt_share(tmp_path: Path) -> None:
    runner = CliRunner()
    key_file = tmp_path / "master.bin"
    key_file.write_bytes(KEY)
    out_dir = tmp_path / "shares"
    _export(runner, key_file, 3, 2, out_dir)

    files = sorted(out_dir.glob("share*.hex"))
    assert len(files) == 3
    files[0].write_text("zz")  # corrupt one
    result = _import(runner, files[1:], tmp_path / "recovered.bin")
    assert result.exit_code == 0, result.output
    assert (tmp_path / "recovered.bin").read_bytes() == KEY


def test_invalid_threshold(tmp_path: Path) -> None:
    runner = CliRunner()
    key_file = tmp_path / "k"
    key_file.write_bytes(KEY)
    res = runner.invoke(
        cli,
        [
            "key",
            "shard",
            "export",
            "--master-key",
            str(key_file),
            "--n",
            "3",
            "--t",
            "5",
            "--out-dir",
            str(tmp_path / "d"),
        ],
    )
    assert res.exit_code != 0


def test_import_too_few(tmp_path: Path) -> None:
    runner = CliRunner()
    key_file = tmp_path / "key.bin"
    key_file.write_bytes(KEY)
    out_dir = tmp_path / "out"
    _export(runner, key_file, 3, 2, out_dir)
    files = sorted(out_dir.glob("share*.hex"))
    result = _import(runner, [files[0]], tmp_path / "bad.bin")
    assert result.exit_code != 0


def test_import_bad_length(tmp_path: Path) -> None:
    runner = CliRunner()
    key_file = tmp_path / "key.bin"
    key_file.write_bytes(KEY)
    out_dir = tmp_path / "shares"
    _export(runner, key_file, 2, 2, out_dir)
    files = sorted(out_dir.glob("share*.hex"))
    files[1].write_text("00")  # too short
    result = _import(runner, files, tmp_path / "rec.bin")
    assert result.exit_code != 0


def test_import_non_hex(tmp_path: Path) -> None:
    runner = CliRunner()
    key_file = tmp_path / "k.bin"
    key_file.write_bytes(KEY)
    out_dir = tmp_path / "sh"
    _export(runner, key_file, 2, 2, out_dir)
    files = sorted(out_dir.glob("share*.hex"))
    files[0].write_text("zz")  # not hex
    result = _import(runner, files, tmp_path / "r.bin")
    assert result.exit_code != 0
