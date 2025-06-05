# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

import pytest
from click.testing import CliRunner

import zilant_prime_core.cli as cli_mod


@pytest.fixture
def runner():
    return CliRunner()


def test_pack_vault_success(tmp_path, monkeypatch, runner):
    src = tmp_path / "file.txt"
    src.write_text("x")
    dest = src.with_suffix(".zil")

    class Dummy:
        def get_secret(self, path, key):
            assert path == "secret/data/test"
            assert key == "password"
            return "pw"

    monkeypatch.setattr(cli_mod, "VaultClient", lambda: Dummy())
    monkeypatch.setattr(
        cli_mod,
        "_ask_pwd",
        lambda *a, **k: (_ for _ in ()).throw(Exception("should not prompt")),
    )
    res = runner.invoke(cli_mod.cli, ["pack", str(src), "--vault-path", "secret/data/test"])
    assert res.exit_code == 0
    assert dest.exists()


def test_pack_vault_error_fallback(tmp_path, monkeypatch, runner):
    src = tmp_path / "file.txt"
    src.write_text("x")
    dest = src.with_suffix(".zil")

    class Dummy:
        def get_secret(self, path, key):
            raise KeyError("fail")

    monkeypatch.setattr(cli_mod, "VaultClient", lambda: Dummy())
    monkeypatch.setattr(cli_mod, "_ask_pwd", lambda *a, **k: "pw")
    res = runner.invoke(cli_mod.cli, ["pack", str(src), "--vault-path", "secret/data/foo"])
    assert "Vault error" in res.output
    assert res.exit_code == 0
    assert dest.exists()


def test_pack_vault_ignored_when_password_flag(tmp_path, monkeypatch, runner):
    src = tmp_path / "file.txt"
    src.write_text("x")
    dest = src.with_suffix(".zil")

    def fail():
        raise AssertionError("VaultClient should not be instantiated")

    monkeypatch.setattr(cli_mod, "VaultClient", lambda: fail())
    res = runner.invoke(
        cli_mod.cli,
        ["pack", str(src), "-p", "cmd", "--vault-path", "secret/data/foo"],
    )
    assert res.exit_code == 0
    assert dest.exists()


def test_pack_missing_both(tmp_path, runner):
    src = tmp_path / "file.txt"
    src.write_text("x")
    res = runner.invoke(cli_mod.cli, ["pack", str(src)])
    assert res.exit_code == 1
    assert "Missing password" in res.output
