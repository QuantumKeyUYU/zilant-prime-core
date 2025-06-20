import os
from click.testing import CliRunner
from pathlib import Path

from zilant_prime_core.cli import cli


def test_hsm_workflow(tmp_path):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # init
        res = runner.invoke(cli, ["hsm", "init"])
        assert res.exit_code == 0
        assert os.path.exists("lock.json")
        assert os.path.exists("counter.txt")

        # create master key
        mk = tmp_path / "master.key"
        mk.write_bytes(b"secret")
        # seal
        res = runner.invoke(
            cli,
            [
                "hsm",
                "seal",
                "--master-key",
                str(mk),
                "--threshold",
                "2",
                "--shares",
                "3",
                "--output-dir",
                "shards",
            ],
        )
        assert res.exit_code == 0
        assert os.path.exists("shards/shard_1.hex")

        # unseal
        res = runner.invoke(
            cli,
            ["hsm", "unseal", "--input-dir", "shards", "--output-file", "out.key"],
        )
        assert res.exit_code == 0
        out = Path("out.key")
        assert out.exists()
        assert out.read_bytes() == b"secret"

        # status
        res = runner.invoke(cli, ["hsm", "status"])
        assert res.exit_code == 0
        assert "lock.json" in res.output
        assert "counter:" in res.output
