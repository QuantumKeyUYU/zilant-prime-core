# src/zilant_prime_core/utils/__init__.py

# SPDX-FileCopyrightText: 2024–2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

from __future__ import annotations

# Константы для AEAD/KDF и контейнера
from .constants import (
    DEFAULT_KEY_LENGTH,
    DEFAULT_NONCE_LENGTH,
    DEFAULT_SALT_LENGTH,
    HEADER_FMT,
    HEADER_SIZE,
    MAGIC,
    VERSION,
)

# Утилиты кодирования
from .formats import from_b64, from_hex, to_b64, to_hex

# Стандартные логгеры
from .logging import get_file_logger, get_logger

# Защищённый логгер AES-GMAC
from .secure_logging import SecureLogger, get_secure_logger

__all__ = [
    # constants.py
    "DEFAULT_KEY_LENGTH",
    "DEFAULT_NONCE_LENGTH",
    "DEFAULT_SALT_LENGTH",
    "HEADER_FMT",
    "HEADER_SIZE",
    "MAGIC",
    "VERSION",
    # formats.py
    "from_b64",
    "from_hex",
    "to_b64",
    "to_hex",
    # logging.py
    "get_logger",
    "get_file_logger",
    # secure_logging.py
    "SecureLogger",
    "get_secure_logger",
]
