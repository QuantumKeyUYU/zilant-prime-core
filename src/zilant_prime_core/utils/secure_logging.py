# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

from __future__ import annotations

import base64
import os
import secrets
from typing import Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

__all__ = ["SecureLogger", "get_secure_logger"]


class SecureLogger:
    """Логгер с AES-GCM и защитой от log-injection."""

    def __init__(self, key: Optional[bytes] = None, log_path: str = "secure.log") -> None:
        raw: Optional[bytes] = key or os.environ.get("ZILANT_LOG_KEY")  # type: ignore[assignment]
        if isinstance(raw, str):
            raw = base64.urlsafe_b64decode(raw.encode())
        if not isinstance(raw, (bytes, bytearray)) or len(raw) != 32:
            raise ValueError("Log key must be 32 bytes")
        self._aesgcm = AESGCM(raw)
        self.log_path = log_path

    def _sanitize(self, msg: str) -> str:
        # Экранируем \n и \r, убираем непечатаемые
        escaped = msg.replace("\n", "\\n").replace("\r", "\\r")
        return "".join(ch for ch in escaped if 32 <= ord(ch) < 127)

    def log(self, msg: str, level: str = "INFO") -> None:
        sanitized = self._sanitize(msg)
        nonce = secrets.token_bytes(12)
        ct = self._aesgcm.encrypt(nonce, sanitized.encode("utf-8"), None)
        entry = b"|".join(
            [
                base64.b64encode(nonce),
                base64.b64encode(ct),
                level.encode("ascii"),
            ]
        )
        # убеждаемся, что каталог существует
        directory = os.path.dirname(self.log_path) or "."
        os.makedirs(directory, exist_ok=True)
        with open(self.log_path, "ab") as f:
            f.write(entry + b"\n")

    def read_logs(self) -> list[tuple[str, str]]:
        out: list[tuple[str, str]] = []
        with open(self.log_path, "rb") as f:
            for line in f:
                n_b64, ct_b64, lvl = line.rstrip(b"\n").split(b"|")
                nonce = base64.b64decode(n_b64)
                ct = base64.b64decode(ct_b64)
                msg = self._aesgcm.decrypt(nonce, ct, None).decode("utf-8")
                out.append((lvl.decode("ascii"), msg))
        return out


_default: Optional[SecureLogger] = None


def get_secure_logger(key: Optional[bytes] = None, log_path: str = "secure.log") -> SecureLogger:
    """
    Возвращает Singleton SecureLogger.
    При первом вызове генерирует или принимает ключ.
    """
    global _default
    if _default is None:
        if key is None and "ZILANT_LOG_KEY" not in os.environ:
            os.environ["ZILANT_LOG_KEY"] = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
        _default = SecureLogger(key=key, log_path=log_path)
    return _default
