import json
from click.testing import CliRunner
from zilant_prime_core.cli import cli
from pathlib import Path


def test_unpack_jitter_outputs_json(tmp_path: Path, monkeypatch):
    container = tmp_path / "foo.zil"
    container.write_bytes(b"bar.txt\nhello")
    monkeypatch.setattr("time.sleep", lambda x: None)
    runner = CliRunner()
    result = runner.invoke(cli, ["unpack", str(container), "-p", "pwd"])
    assert result.exit_code == 0
    data = json.loads(result.output.strip())
    assert data["result"] == "OK"
    assert data["canary"] is True


def test_unpack_jitter_file_created(tmp_path: Path, monkeypatch):
    container = tmp_path / "foo.zil"
    container.write_bytes(b"bar.txt\nhello")
    monkeypatch.setattr("time.sleep", lambda x: None)
    runner = CliRunner()
    runner.invoke(cli, ["unpack", str(container), "-p", "pwd"])
    out = tmp_path / "bar.txt"
    assert out.exists()
    assert out.read_bytes() == b"hello"
