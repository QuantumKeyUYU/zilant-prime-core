# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

import shutil
import subprocess

import zilant_prime_core.utils.tpm_attestation as tpm


class DummyProcess:
    def __init__(self, returncode: int):
        self.returncode = returncode
        self.stdout = b""
        self.stderr = b""


def create_dummy_pcr(tmp_path):
    pcr_dir = tmp_path / "pcr"
    pcr_dir.mkdir()
    for i in range(2):
        pcr_file = pcr_dir / str(i)
        pcr_file.write_bytes(b"dummy_pcr_%d" % i)
    return pcr_dir


def test_no_tpm_util(monkeypatch, tmp_path):
    monkeypatch.setattr(shutil, "which", lambda x: None)
    assert tpm.attest_via_tpm() is False


def test_pcr_dir_missing(monkeypatch):
    monkeypatch.setenv("ZILANT_PCR_PATH", "/nonexistent/path")
    monkeypatch.setattr(shutil, "which", lambda x: "/usr/bin/tpm2_quote")
    assert tpm.attest_via_tpm() is False


def test_pcr_dir_empty(monkeypatch, tmp_path):
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    monkeypatch.setenv("ZILANT_PCR_PATH", str(empty_dir))
    monkeypatch.setattr(shutil, "which", lambda x: "/usr/bin/tpm2_quote")
    assert tpm.attest_via_tpm() is False


def test_tpm_quote_fails(monkeypatch, tmp_path):
    pcrd = create_dummy_pcr(tmp_path)
    monkeypatch.setenv("ZILANT_PCR_PATH", str(pcrd))
    monkeypatch.setattr(shutil, "which", lambda x: "/usr/bin/tpm2_quote")
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: DummyProcess(returncode=1))
    assert tpm.attest_via_tpm() is False


def test_tpm_quote_no_file(monkeypatch, tmp_path):
    pcrd = create_dummy_pcr(tmp_path)
    monkeypatch.setenv("ZILANT_PCR_PATH", str(pcrd))
    monkeypatch.setattr(shutil, "which", lambda x: "/usr/bin/tpm2_quote")
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: DummyProcess(returncode=0))
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
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: DummyProcess(returncode=0))
    assert tpm.attest_via_tpm() is True
