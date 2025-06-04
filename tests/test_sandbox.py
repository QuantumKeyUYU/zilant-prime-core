import os

from click.testing import CliRunner

from zilant_prime_core.cli import _maybe_sandbox


def test_maybe_sandbox(monkeypatch):
    called = {}

    monkeypatch.setattr("shutil.which", lambda x: "/usr/bin/runsc")

    def fake_execvp(cmd, args):
        called["args"] = args
        raise SystemExit

    monkeypatch.setattr(os, "execvp", fake_execvp)
    with CliRunner().isolated_filesystem():
        try:
            _maybe_sandbox()
        except SystemExit:
            pass
    assert called["args"][0] == "runsc"
