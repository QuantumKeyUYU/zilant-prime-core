import json
from pathlib import Path

from click.testing import CliRunner

runner = CliRunner()


def test_unpack_jitter(monkeypatch, tmp_path: Path):
    cont = tmp_path / "c.zil"
    cont.write_bytes(b"x\nhello")

    sleep_calls = {}

    def fake_sleep(val):
        if val < 1:
            sleep_calls["val"] = val

    from zilant_prime_core import cli as cli_mod

    monkeypatch.setattr(cli_mod.time, "sleep", fake_sleep)
    monkeypatch.setattr(cli_mod.random, "uniform", lambda a, b: 0.02)

    result = runner.invoke(cli_mod.cli, ["unpack", str(cont), "-p", "pw"])
    assert result.exit_code == 0, result.output
    last_line = result.output.strip().splitlines()[-1]
    data = json.loads(last_line)
    assert data == {"result": "OK", "canary": True}
    assert 0 < sleep_calls["val"] <= 0.05
