# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

# tests/test_secure_logger_branches.py

import os
import secrets

import pytest

from zilant_prime_core.utils.secure_logging import SecureLogger, get_secure_logger


def test_secure_logger_accepts_raw_bytes_key(tmp_path):
    # Передаём ключ как raw bytes
    key = secrets.token_bytes(32)
    log_file = str(tmp_path / "s.log")
    slog = SecureLogger(key=key, log_path=log_file)
    slog.log("payload", "LEVEL")
    entries = slog.read_logs()
    assert entries == [("LEVEL", "payload")]


def test_secure_logger_invalid_key_raises():
    # Неправильная длина ключа
    with pytest.raises(ValueError):
        SecureLogger(key=b"short", log_path="x.log")


def test_get_secure_logger_singleton(monkeypatch, tmp_path):
    # Заставляем не генерировать новый при повторном вызове
    os.environ.pop("ZILANT_LOG_KEY", None)
    path = str(tmp_path / "one.log")
    slog1 = get_secure_logger(log_path=path)
    slog2 = get_secure_logger(log_path=path)
    assert slog1 is slog2
