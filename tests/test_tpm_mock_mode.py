import importlib

from click.testing import CliRunner


def test_cli_runs_without_tpm(tmp_path, monkeypatch):
    monkeypatch.setenv("ZILANT_NO_TPM", "1")
    import zilant_prime_core.cli as cli_mod
    import zilant_prime_core.utils.attest as attest_mod
    import zilant_prime_core.utils.tpm_counter as tpm_counter_mod

    importlib.reload(tpm_counter_mod)
    importlib.reload(attest_mod)
    importlib.reload(cli_mod)

    src = tmp_path / "foo.txt"
    src.write_text("data")
    runner = CliRunner()
    result = runner.invoke(cli_mod.cli, ["pack", str(src), "-p", "pw"])
    assert result.exit_code == 0
    out_file = tmp_path / "foo.zil"
    assert out_file.exists()
