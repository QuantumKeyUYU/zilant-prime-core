# SPDX-FileCopyrightText: 2024‑2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT
"""
Пакет util‑ов ядра ZILANT Prime™.
"""

from __future__ import annotations

# ──────────────────────── Public constants ──────────────────────────
from .constants import (
    DEFAULT_KEY_LENGTH,
    DEFAULT_NONCE_LENGTH,
    DEFAULT_SALT_LENGTH,
    HEADER_FMT,
    HEADER_SIZE,
    MAGIC,
    VERSION,
)
from .file_monitor import start_file_monitor

# ───────────────────────── Encode / decode ──────────────────────────
from .formats import from_b64, from_hex, to_b64, to_hex

# ───────────────────────────── Logging ──────────────────────────────
from .logging import get_file_logger, get_logger
from .secure_logging import SecureLogger, get_secure_logger

# ───────────────────────── Vault integration ────────────────────────
from .vault_client import VaultClient


def get_tpm_key() -> bytes:  # pragma: no cover
    """Заглушка для Stage 0: Для будущей интеграции с TPM (tpm2_unseal)"""
    raise NotImplementedError("TPM not configured yet")


__all__: list[str] = [
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
    # vault_client.py
    "VaultClient",
    # file_monitor.py
    "start_file_monitor",
    "get_tpm_key",
]
