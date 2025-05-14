"""
Small smoke-test for CLI — покрывает строки в cli.py,
в том числе промпт-логики Click’а.
"""
from pathlib import Path

from click.testing import CliRunner

from zilant_prime_core.cli import cli


def test_cli_pack_and_unpack(tmp_path: Path):
    runner = CliRunner(mix_stderr=False)

    # ── файл-источник ──
    src = tmp_path / "song.txt"
    src.write_text("Born to be a dragon!")

    # ── pack ──
    pack_input = "s3cr3t\ns3cr3t\n"  # пароль + confirmation
    result = runner.invoke(cli, ["pack", str(src), "-p", "-"], input=pack_input)
    assert result.exit_code == 0, result.output
    container = src.with_suffix(".zil")
    assert container.exists()

    # ── unpack ──
    unpack_input = "s3cr3t\n"
    dest = tmp_path / "extracted"
    result = runner.invoke(
        cli,
        ["unpack", str(container), "-p", "-", "-d", str(dest)],
        input=unpack_input,
    )
    assert result.exit_code == 0, result.output
    extracted = dest / src.name
    assert extracted.read_text() == "Born to be a dragon!"
