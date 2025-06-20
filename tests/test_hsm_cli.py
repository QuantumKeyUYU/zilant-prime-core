import json
import re
from click.testing import CliRunner
from pathlib import Path

from zilant_prime_core.cli import cli
from zilant_prime_core.utils import counter as uc


def test_init(tmp_path):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        res = runner.invoke(cli, ["hsm", "init"])
        assert res.exit_code == 0
        cwd = Path.cwd()
        lock = cwd / "lock.json"
        counter = cwd / "counter.txt"
        assert lock.exists()
        assert counter.exists()
        info = json.loads(lock.read_text())
        assert isinstance(info.get("created"), int)
        assert counter.read_text() == "0"


def test_seal(tmp_path):
    runner = CliRunner()
    master = tmp_path / "master.key"
    master.write_text("deadbeef")
    out_dir = tmp_path / "shards"
    res = runner.invoke(
        cli,
        [
            "hsm",
            "seal",
            "--master-key",
            str(master),
            "--threshold",
            "2",
            "--shares",
            "3",
            "--output-dir",
            str(out_dir),
        ],
    )
    assert res.exit_code == 0
    shards = [out_dir / f"shard_{i}.hex" for i in range(1, 4)]
    for sh in shards:
        assert sh.exists()
        assert re.fullmatch(r"[0-9a-f]+", sh.read_text().strip())


def test_unseal(tmp_path):
    runner = CliRunner()
    master = tmp_path / "master.key"
    master.write_text("deadbeef")
    out_dir = tmp_path / "shards"
    runner.invoke(
        cli,
        [
            "hsm",
            "seal",
            "--master-key",
            str(master),
            "--threshold",
            "2",
            "--shares",
            "3",
            "--output-dir",
            str(out_dir),
        ],
    )
    out_file = tmp_path / "out.key"
    res = runner.invoke(
        cli,
        ["hsm", "unseal", "--input-dir", str(out_dir), "--output-file", str(out_file)],
    )
    assert res.exit_code == 0
    assert out_file.read_text() == "deadbeef"


def test_status(tmp_path, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        res = runner.invoke(cli, ["hsm", "init"])
        assert res.exit_code == 0
        counter_file = Path("counter.txt").resolve()
        backup_file = counter_file.with_name("counter.bak")
        monkeypatch.setattr(uc, "COUNTER_FILE", counter_file)
        monkeypatch.setattr(uc, "BACKUP_COUNTER_FILE", backup_file)
        uc.increment_counter()
        res = runner.invoke(cli, ["hsm", "status"])
        assert res.exit_code == 0
        data = json.loads(res.output)
        assert isinstance(data.get("created"), int)
        assert data.get("counter") == 1
