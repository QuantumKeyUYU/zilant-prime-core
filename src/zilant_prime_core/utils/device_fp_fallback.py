# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
"""Fallback device fingerprint utilities."""

from __future__ import annotations

import time
from pathlib import Path

from crypto_core import hash_sha3

__all__ = ["device_fp_fallback"]


def device_fp_fallback(cpuinfo_path: str = "/proc/cpuinfo") -> str:
    """Return SHA3-256 fingerprint of ``cpuinfo_path`` or monotonic fallback."""
    try:
        data = Path(cpuinfo_path).read_bytes()
    except Exception:
        data = str(time.monotonic_ns()).encode()
    digest = hash_sha3(data)
    return digest.hex()
