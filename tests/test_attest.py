import subprocess

import pytest

from attest import attestation_check


def test_attest_no_tpm(monkeypatch):
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: (_ for _ in ()).throw(FileNotFoundError()))
    assert attestation_check() is False


def test_attest_success(monkeypatch):
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: None)
    assert attestation_check() is True


def test_attest_fail(monkeypatch):
    def bad_run(*args, **kwargs):
        raise subprocess.CalledProcessError(1, "tpm2_quote")

    monkeypatch.setattr(subprocess, "run", bad_run)
    with pytest.raises(RuntimeError):
        attestation_check()
