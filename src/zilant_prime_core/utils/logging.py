# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

import hashlib
import hmac
import json
import logging
import os
import tempfile
import time
from pathlib import Path
from typing import Optional, Union

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from zilant_prime_core.utils.secure_logging import SecureLogger, get_secure_logger

if os.name == "nt":
    base = Path(os.getenv("LOCALAPPDATA", tempfile.gettempdir())) / "ZilantPrime"
    LOG_PATH = str(base / "incident.enc")
    USB_LOG_PATH = str(base / "incident_backup.enc")
else:
    LOG_PATH = "/var/log/.pseudohsm_incident.enc"
    USB_LOG_PATH = "/mnt/usb/incident_backup.enc"


def __lock_path() -> str:
    """Return path to snapshot lock file in a cross-platform manner."""
    if os.name == "nt":
        base = Path(os.getenv("LOCALAPPDATA", tempfile.gettempdir())) / "ZilantPrime"
    else:
        base = Path("/var/lock")
        if not base.exists():
            base = Path(tempfile.gettempdir())
    return str(base / "pseudohsm.lock")


def _hmac_sha256(key: bytes, data: bytes) -> bytes:
    return hmac.new(key, data, hashlib.sha256).digest()


__all__ = ["get_logger", "get_file_logger"]


def get_logger(
    name: str, *, secure: Optional[bool] = None, log_path: Optional[str] = None
) -> Union[logging.Logger, SecureLogger]:
    """
    Возвращает либо обычный logging.Logger, либо SecureLogger, в зависимости
    от флага secure или переменной среды ZILANT_SECURE_LOG=1.

    - name: имя логгера (используется только для обычного Logger).
    - secure: если True, возвращаем SecureLogger. Если False, обычный Logger.
      Если None, проверяем ZILANT_SECURE_LOG в окружении.
    - log_path: путь до файла лога (для SecureLogger). Если None и нужен SecureLogger,
      используется “secure.log” в текущей директории.
    """
    want_secure = False
    if secure is True:
        want_secure = True
    elif secure is False:
        want_secure = False
    else:
        # secure is None → смотрим окружение
        want_secure = os.getenv("ZILANT_SECURE_LOG", "") == "1"

    if want_secure:
        # Гарантируем, что log_path будет непустой строкой
        path = log_path or "secure.log"
        return get_secure_logger(log_path=path)

    # Обычный Logger
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def get_file_logger(
    name: str, file_path: str, *, secure: Optional[bool] = None, log_path: Optional[str] = None
) -> Union[logging.Logger, SecureLogger]:
    """
    Возвращает файловый логгер:
    - Если secure=True или ZILANT_SECURE_LOG=1, возвращаем SecureLogger,
      настроенный на запись в file_path. В этом случае параметр file_path
      игнорируется, вместо него используется log_path (или “secure.log”).
    - Иначе возвращаем обычный logging.Logger с FileHandler → file_path.
    """
    want_secure = False
    if secure is True:
        want_secure = True
    elif secure is False:
        want_secure = False
    else:
        want_secure = os.getenv("ZILANT_SECURE_LOG", "") == "1"

    if want_secure:
        # Для SecureLogger логический путь – это log_path
        path = log_path or "secure.log"
        return get_secure_logger(log_path=path)

    # Обычный файловый логгер
    logger = logging.getLogger(name)
    if not logger.handlers:
        fh = logging.FileHandler(file_path)
        fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s"))
        logger.addHandler(fh)
        logger.setLevel(logging.INFO)
    return logger


def log_event(event_type: str, details: dict[str, object], sk1_handle: int) -> None:
    from .crypto_wrapper import get_sk_bytes

    key = _hmac_sha256(get_sk_bytes(sk1_handle), b"log")
    nonce = os.urandom(12)
    data = json.dumps({"timestamp": int(time.time()), "event_type": event_type, "details": details}).encode()
    ciphertext = AESGCM(key).encrypt(nonce, data, None)
    for path in [LOG_PATH, USB_LOG_PATH]:
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, "ab") as f:
                f.write(nonce + ciphertext)
        except Exception:
            continue


def self_destruct_all() -> None:
    targets = [
        str(Path.home() / ".zilant" / ".hidden_counter"),
        str(Path.home() / ".zilant" / ".key_store"),
        str(Path.home() / ".zilant" / ".container"),
        __lock_path(),
    ]
    for path in targets:
        try:
            if os.path.exists(path):
                with open(path, "r+b") as f:
                    f.write(os.urandom(len(f.read())))
                    f.flush()
                    os.fsync(f.fileno())
        except Exception:
            pass
    try:
        with open(targets[-1], "w") as f:
            f.write('{"status":"OK","message":"Data intact"}')
    except Exception:
        pass
    try:
        from .crypto_wrapper import get_sk_bytes

        key = _hmac_sha256(get_sk_bytes(1), b"log")
        nonce = os.urandom(12)
        data = json.dumps({"timestamp": int(time.time()), "event": "SELF_DESTRUCT"}).encode()
        ciphertext = AESGCM(key).encrypt(nonce, data, None)
        with open(LOG_PATH, "ab") as f:
            f.write(nonce + ciphertext)
        open(LOG_PATH, "wb").close()
    except Exception:
        pass
    print("Ошибка доступа. Проверьте введённые данные.")
    os._exit(1)
