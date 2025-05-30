# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

import secrets

import pytest

from zilant_prime_core.utils.secure_logging import SecureLogger, get_secure_logger


def test_secure_logger_accepts_raw_bytes_key(tmp_path):
    key = secrets.token_bytes(32)
    log_file = str(tmp_path / "s.log")
    slog = SecureLogger(key=key, log_path=log_file)
    slog.log("payload", "LEVEL")
    entries = slog.read_logs()
    assert entries == [("LEVEL", "payload")]


def test_secure_logger_invalid_key_raises():
    # Ключ должен быть ровно 32 байта, иначе ошибка
    with pytest.raises(ValueError):
        SecureLogger(key=b"short", log_path="x.log")


def test_get_secure_logger_singleton_isolation(tmp_path, monkeypatch):
    # Сброс singleton перед тестом, чтобы не было конфликтов с другими тестами
    import zilant_prime_core.utils.secure_logging as sl

    monkeypatch.delenv("ZILANT_LOG_KEY", raising=False)
    sl._default = None

    log1 = str(tmp_path / "l1.log")
    log2 = str(tmp_path / "l2.log")
    slog1 = get_secure_logger(log_path=log1)
    slog2 = get_secure_logger(log_path=log2)
    assert slog1 is slog2
    # Проверяем, что файл выставлен как первый log_path
    assert slog1.log_path == log1


def test_secure_logger_fields_update(tmp_path):
    key = secrets.token_bytes(32)
    log_file = str(tmp_path / "fields.log")
    slog = SecureLogger(key=key, log_path=log_file)
    slog.log("test", "L1", foo="bar", id=7)
    entries = slog.read_logs()
    assert ("L1", "test") in entries
    # Проверяем, что дополнительные поля корректно логируются
    assert any(
        tup[0] == "L1"
        and tup[1] == "test"
        and isinstance(tup[2], dict)
        and tup[2]["foo"] == "bar"
        and tup[2]["id"] == 7
        for tup in entries
        if len(tup) == 3
    )


def test_secure_logger_read_logs_no_file(tmp_path):
    key = secrets.token_bytes(32)
    log_file = str(tmp_path / "no_such_file.log")
    slog = SecureLogger(key=key, log_path=log_file)
    assert slog.read_logs() == []


def test_secure_logger_handles_corrupt_log(tmp_path):
    key = secrets.token_bytes(32)
    log_file = str(tmp_path / "corrupt.log")
    slog = SecureLogger(key=key, log_path=log_file)
    # Запишем в лог невалидную строку
    with open(log_file, "ab") as f:
        f.write(b"not|a|valid|log\n")
    slog.log("hello", "INFO")
    entries = slog.read_logs()
    # Невалидная строка пропускается, настоящая логируется
    assert ("INFO", "hello") in entries
