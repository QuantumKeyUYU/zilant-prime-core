# tests/test_cli_commands_enhanced.py

import json
import yaml
from click.testing import CliRunner
from types import SimpleNamespace

from zilant_prime_core.cli_commands import _emit, shard_cmd


def test_emit_json(capsys):
    ctx = SimpleNamespace(obj={"output": "json"})
    _emit(ctx, {"foo": "bar"})
    out = capsys.readouterr().out
    # valid JSON with indent
    assert json.loads(out) == {"foo": "bar"}


def test_emit_yaml(capsys):
    ctx = SimpleNamespace(obj={"output": "yaml"})
    _emit(ctx, {"foo": "bar"})
    out = capsys.readouterr().out
    assert yaml.safe_load(out) == {"foo": "bar"}


def test_emit_default(capsys):
    ctx = SimpleNamespace(obj={"output": None})
    _emit(ctx, {"k": "v"})
    out = capsys.readouterr().out.strip()
    assert out == "v"


def test_shard_import_missing_meta(tmp_path):
    runner = CliRunner()
    inp = tmp_path / "in"
    inp.mkdir()
    # никакого meta.json
    result = runner.invoke(shard_cmd, ["import", "--input-dir", str(inp), "--output-file", str(tmp_path / "out.bin")])
    assert result.exit_code != 0
    assert "meta.json missing in input directory" in result.output
