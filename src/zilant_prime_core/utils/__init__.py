# SPDX-FileCopyrightText: 2024‑2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT
"""
Пакет util‑ов ядра ZILANT Prime™.
"""

from __future__ import annotations

from .anti_snapshot import detect_snapshot

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
from .counter import increment_counter, read_counter, write_counter

# ───────────────────────── Pseudo-HSM placeholders ──────────────────────────
from .device_fp import get_device_fingerprint
from .device_fp_fallback import device_fp_fallback

# ───────────────────────── Encode / decode ──────────────────────────
from .formats import from_b64, from_hex, to_b64, to_hex
from .hash_challenge import generate_daily_challenge
from .honeyfile import HoneyfileError, check_tmp_for_honeyfiles

# ───────────────────────────── Logging ──────────────────────────────
from .logging import get_file_logger, get_logger
from .root_guard import assert_safe_or_die, is_device_rooted
from .screen_guard import ScreenGuard, ScreenGuardError, guard
from .secure_logging import SecureLogger, get_secure_logger
from .shard_secret import recover_secret, split_secret

# ───────────────────────── Vault integration ────────────────────────
from .vault_client import VaultClient

__all__: list[str] = [
    "DEFAULT_KEY_LENGTH",
    "DEFAULT_NONCE_LENGTH",
    "DEFAULT_SALT_LENGTH",
    "HEADER_FMT",
    "HEADER_SIZE",
    "MAGIC",
    "VERSION",
    "HoneyfileError",
    "ScreenGuard",
    "ScreenGuardError",
    "SecureLogger",
    "VaultClient",
    "assert_safe_or_die",
    "check_tmp_for_honeyfiles",
    "detect_snapshot",
    "device_fp_fallback",
    "from_b64",
    "from_hex",
    "generate_daily_challenge",
    "get_device_fingerprint",
    "get_file_logger",
    "get_logger",
    "get_secure_logger",
    "guard",
    "increment_counter",
    "is_device_rooted",
    "read_counter",
    "recover_secret",
    "split_secret",
    "to_b64",
    "to_hex",
    "write_counter",
]
