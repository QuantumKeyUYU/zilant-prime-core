# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

import base64
import secrets

from zilant_prime_core.utils.secure_logging import SecureLogger, get_secure_logger


def test_secure_logger_roundtrip(tmp_path, monkeypatch):
    # фиксированный ключ
    key = secrets.token_bytes(32)
    monkeypatch.setenv("ZILANT_LOG_KEY", base64.urlsafe_b64encode(key).decode())
    log_file = tmp_path / "sec.log"
    slog = SecureLogger(log_path=str(log_file))
    slog.log("Test\nInjection", "TEST")
    entries = slog.read_logs()
    assert entries == [("TEST", "Test\\nInjection")]


def test_get_secure_logger_singleton(tmp_path):
    # Должен вернуть один и тот же объект
    slog1 = get_secure_logger(str(tmp_path / "l1.log"))
    slog2 = get_secure_logger(str(tmp_path / "l2.log"))
    assert slog1 is slog2
