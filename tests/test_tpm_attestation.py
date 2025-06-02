# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

import shutil
import subprocess

import pytest

import zilant_prime_core.utils.tpm_attestation as tpm


class DummyProcess:
    def __init__(self, returncode: int):
        self.returncode = returncode
        self.stdout = b""
        self.stderr = b""


@pytest.fixture(autouse=True)
def isolate_env(tmp_path, monkeypatch):
    monkeypatch.delenv("ZILANT_PCR_PATH", raising=False)
    monkeypatch.delenv("ZILANT_QUOTE_FILE", raising=False)
    monkeypatch.delenv("ZILANT_TPM_KEY_CTX", raising=False)
    monkeypatch.delenv("ZILANT_TPM_PUBKEY_CTX", raising=False)
    yield
    for key in ["ZILANT_PCR_PATH", "ZILANT_QUOTE_FILE", "ZILANT_TPM_KEY_CTX", "ZILANT_TPM_PUBKEY_CTX"]:
        monkeypatch.delenv(key, raising=False)


def test_no_tpm_util(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda x: None)
    assert tpm.attest_via_tpm() is None


def test_pcr_dir_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(shutil, "which", lambda x: "/usr/bin/tpm2_quote")
    monkeypatch.setenv("ZILANT_PCR_PATH", str(tmp_path / "nonexistent"))
    assert tpm.attest_via_tpm() is False


def test_pcr_dir_empty(monkeypatch, tmp_path):
    d = tmp_path / "pcrs"
    d.mkdir()
    monkeypatch.setattr(shutil, "which", lambda x: "/usr/bin/tpm2_quote")
    monkeypatch.setenv("ZILANT_PCR_PATH", str(d))
    assert tpm.attest_via_tpm() is False


def create_dummy_pcr(tmp_path):
    d = tmp_path / "pcrs"
    d.mkdir()
    for i in range(3):
        f = d / str(i)
        f.write_bytes(bytes.fromhex("00" * 32))
    return d


def test_tpm_quote_fails(monkeypatch, tmp_path):
    pcrd = create_dummy_pcr(tmp_path)
    monkeypatch.setattr(shutil, "which", lambda x: "/usr/bin/tpm2_quote")
    monkeypatch.setenv("ZILANT_PCR_PATH", str(pcrd))
    dummy = DummyProcess(returncode=1)
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: dummy)
    assert tpm.attest_via_tpm() is False


def test_tpm_quote_no_file(monkeypatch, tmp_path):
    pcrd = create_dummy_pcr(tmp_path)
    monkeypatch.setattr(shutil, "which", lambda x: "/usr/bin/tpm2_quote")
    monkeypatch.setenv("ZILANT_PCR_PATH", str(pcrd))

    def fake_run(cmd, **kwargs):
        if "tpm2_quote" in cmd:
            return DummyProcess(returncode=0)
        return DummyProcess(returncode=0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    quote_file = tmp_path / "tpm_quote.bin"
    monkeypatch.setenv("ZILANT_QUOTE_FILE", str(quote_file))
    assert tpm.attest_via_tpm() is False


def test_tpm_verify_fails(monkeypatch, tmp_path):
    pcrd = create_dummy_pcr(tmp_path)
    monkeypatch.setattr(shutil, "which", lambda x: "/usr/bin/tpm2_quote")
    monkeypatch.setenv("ZILANT_PCR_PATH", str(pcrd))
    quote_file = tmp_path / "tpm_quote.bin"
    monkeypatch.setenv("ZILANT_QUOTE_FILE", str(quote_file))
    quote_file.write_bytes(b"dummy")

    def fake_run(cmd, **kwargs):
        if "tpm2_quote" in cmd:
            return DummyProcess(returncode=0)
        return DummyProcess(returncode=1)

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert tpm.attest_via_tpm() is False


def test_tpm_success(monkeypatch, tmp_path):
    pcrd = create_dummy_pcr(tmp_path)
    monkeypatch.setattr(shutil, "which", lambda x: "/usr/bin/tpm2_quote")
    monkeypatch.setenv("ZILANT_PCR_PATH", str(pcrd))
    quote_file = tmp_path / "tpm_quote.bin"
    monkeypatch.setenv("ZILANT_QUOTE_FILE", str(quote_file))
    quote_file.write_bytes(b"dummy")
    sig_file = tmp_path / "tpm_quote.bin.sig"
    sig_file.write_bytes(b"dummy")

    def fake_run(cmd, **kwargs):
        return DummyProcess(returncode=0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert tpm.attest_via_tpm() is True
