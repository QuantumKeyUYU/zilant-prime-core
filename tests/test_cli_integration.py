import os
from pathlib import Path
import pytest
from click.testing import CliRunner
from zilant_prime_core.cli import cli


def test_cli_pack_and_unpack(tmp_path: Path):
    runner = CliRunner()

    # ── исходный файл ──
    src = tmp_path / "song.txt"
    src.write_text("Born to be a dragon!")

    # ── pack ──
    pack_input = "s3cr3t\ns3cr3t\n"  # пароль + подтверждение
    result = runner.invoke(cli, ["pack", str(src), "-p", "-"], input=pack_input)
    assert result.exit_code == 0
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
    assert result.exit_code == 0
    # проверяем, что содержимое восстановлено
    assert (dest / "song.txt").read_text() == "Born to be a dragon!"


def test_cli_wrong_password(tmp_path: Path):
    runner = CliRunner()
    src = tmp_path / "secret.txt"
    src.write_text("TOP SECRET")

    # pack с разными паролями
    result = runner.invoke(cli, ["pack", str(src), "-p", "-"], input="foo\nbar\n")
    assert result.exit_code != 0
