# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

import base64
import secrets

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from zilant_prime_core.utils.secure_logging import SecureLogger, get_secure_logger


def test_secure_logger_roundtrip(tmp_path, monkeypatch):
    # фиксированный ключ
    key = secrets.token_bytes(32)
    monkeypatch.setenv("ZILANT_LOG_KEY", base64.urlsafe_b64encode(key).decode())
    log_file = tmp_path / "sec.log"
    slog = SecureLogger(log_path=str(log_file))
    slog.log("Test\nInjection", "TEST")
    entries = slog.read_logs()
    # Проверяем, что расшифровка верная (символы '\n' экранируются)
    assert entries == [("TEST", "Test\\nInjection")]


def test_get_secure_logger_singleton(tmp_path):
    # Должен вернуть один и тот же объект
    log1 = str(tmp_path / "l1.log")
    log2 = str(tmp_path / "l2.log")
    slog1 = get_secure_logger(log_path=log1)
    slog2 = get_secure_logger(log_path=log2)
    assert slog1 is slog2


def test_secure_logger_invalid_line(tmp_path, monkeypatch):
    # Если встретилась строка без корректного base64-формата, пропускаем её без ошибок
    key = secrets.token_bytes(32)
    monkeypatch.setenv("ZILANT_LOG_KEY", base64.urlsafe_b64encode(key).decode())
    log_file = tmp_path / "bad.log"
    with open(log_file, "wb") as f:
        f.write(b"not|base64\n")  # нет разделителя или некорректный base64
        f.write(b"onlyonepart\n")  # нет разделителя '|'
        # некорректная расшифровка (ошибка аутентификации)
        f.write(b"SGVsbG8=|SGVsbG8=\n")
    slog = SecureLogger(log_path=str(log_file))
    # Всё должно быть пропущено без ошибок, возвращаем пустой список
    assert slog.read_logs() == []


def test_secure_logger_invalid_json(tmp_path, monkeypatch):
    # Если расшифрованный фрагмент не валидный JSON, пропускаем
    key = secrets.token_bytes(32)
    monkeypatch.setenv("ZILANT_LOG_KEY", base64.urlsafe_b64encode(key).decode())
    log_file = tmp_path / "badjson.log"
    nonce = secrets.token_bytes(12)
    aesgcm = AESGCM(key)
    ct = aesgcm.encrypt(nonce, b"{invalid json", None)
    with open(log_file, "wb") as f:
        f.write(base64.b64encode(nonce) + b"|" + base64.b64encode(ct) + b"\n")
    slog = SecureLogger(log_path=str(log_file))
    assert slog.read_logs() == []


def test_secure_logger_empty_file(tmp_path, monkeypatch):
    # Пустой файл — это корректная ситуация: возвращаем []
    key = secrets.token_bytes(32)
    monkeypatch.setenv("ZILANT_LOG_KEY", base64.urlsafe_b64encode(key).decode())
    log_file = tmp_path / "empty.log"
    open(log_file, "wb").close()
    slog = SecureLogger(log_path=str(log_file))
    assert slog.read_logs() == []


def test_secure_logger_file_missing(tmp_path, monkeypatch):
    # Если файл отсутствует, возвращаем пустой список
    key = secrets.token_bytes(32)
    monkeypatch.setenv("ZILANT_LOG_KEY", base64.urlsafe_b64encode(key).decode())
    log_file = tmp_path / "absent.log"
    slog = SecureLogger(log_path=str(log_file))
    assert slog.read_logs() == []
