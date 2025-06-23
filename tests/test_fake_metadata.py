# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

from click.testing import CliRunner
from pathlib import Path
import json

from zilant_prime_core.cli import cli
from container import get_metadata


def test_fake_metadata_option(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    src = tmp_path / "a.txt"
    src.write_text("x")
    result = CliRunner().invoke(cli, [
        "pack",
        str(src),
        "-p",
        "x"*32,
        "--fake-metadata",
    ])
    assert result.exit_code == 0
    meta = get_metadata(tmp_path / "a.zil")
    assert meta["owner"] == "anonymous"
    assert meta["origin"] == "N/A"


def test_show_metadata_command(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    src = tmp_path / "b.txt"
    src.write_text("y")
    CliRunner().invoke(cli, ["pack", str(src), "-p", "x"*32, "--fake-metadata"])
    res = CliRunner().invoke(cli, ["uyi", "show-metadata", str(tmp_path / "b.zil")])
    data = json.loads(res.output.strip())
    assert data["owner"] == "anonymous"

