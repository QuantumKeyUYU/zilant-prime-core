# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

import shutil
import subprocess
from pathlib import Path

import pytest

import zilant_prime_core.utils.tpm_attestation as tpm


class DummyProcess:
    def __init__(self, returncode: int):
        self.returncode = returncode
        self.stdout = b""
        self.stderr = b""


@pytest.fixture(autouse=True)
def isolate_env(monkeypatch):
    # Очищаем переменные окружения для чистоты тестов
    for key in ("ZILANT_PCR_PATH", "ZILANT_QUOTE_FILE", "ZILANT_TPM_KEY_CTX", "ZILANT_TPM_PUBKEY_CTX"):
        monkeypatch.delenv(key, raising=False)
    yield
    for key in ("ZILANT_PCR_PATH", "ZILANT_QUOTE_FILE", "ZILANT_TPM_KEY_CTX", "ZILANT_TPM_PUBKEY_CTX"):
        monkeypatch.delenv(key, raising=False)


def create_dummy_pcr(tmp_path):
    # Помощник: создаём три PCR-файла
    d = tmp_path / "pcrs"
    d.mkdir()
    for i in range(3):
        (d / str(i)).write_bytes(b"\x00" * 32)
    return d


def test_quote_cmd_error(monkeypatch, tmp_path):
    # Если tpm2_quote возвращает ошибку (код != 0) → False
    pcrd = create_dummy_pcr(tmp_path)
    monkeypatch.setenv("ZILANT_PCR_PATH", str(pcrd))
    monkeypatch.setattr(shutil, "which", lambda x: "/usr/bin/tpm2_quote")
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: DummyProcess(returncode=1))
    assert tpm.attest_via_tpm() is False


def test_read_quote_error(monkeypatch, tmp_path):
    # Если файл квоты существует, но при чтении PCR попало исключение → False
    pcrd = create_dummy_pcr(tmp_path)
    monkeypatch.setenv("ZILANT_PCR_PATH", str(pcrd))
    quote_file = tmp_path / "tpm_quote.bin"
    quote_file.write_bytes(b"dummy")
    monkeypatch.setattr(shutil, "which", lambda x: "/usr/bin/tpm2_quote")
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: DummyProcess(returncode=0))
    # Заставляем Path.read_bytes бросать исключение
    original_read = Path.read_bytes
    monkeypatch.setattr(Path, "read_bytes", lambda self: (_ for _ in ()).throw(Exception()))
    assert tpm.attest_via_tpm() is False
    monkeypatch.setattr(Path, "read_bytes", original_read)
