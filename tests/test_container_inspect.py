import json
import os
from click.testing import CliRunner

from container import pack_file, read_header
from zilant_prime_core.cli import cli


def test_read_header(tmp_path):
    src = tmp_path / "f.txt"
    src.write_text("hello")
    cont = tmp_path / "f.zil"
    pack_file(src, cont, os.urandom(32))
    meta = read_header(cont)
    assert meta["orig_size"] == 5
    assert meta["mode"] == "classic"


def test_cli_inspect_json(tmp_path):
    src = tmp_path / "f.txt"
    src.write_text("abc")
    cont = tmp_path / "f.zil"
    pack_file(src, cont, os.urandom(32))
    result = CliRunner().invoke(cli, ["--output", "json", "inspect", str(cont)])
    assert result.exit_code == 0
    meta = json.loads(result.output)
    assert meta["orig_size"] == 3
