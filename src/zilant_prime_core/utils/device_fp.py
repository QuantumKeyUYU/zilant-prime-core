# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
"""Device fingerprint helpers for Quantum-Pseudo-HSM."""

from __future__ import annotations

import hashlib
import hmac
import os
import platform

_HMAC_KEY = b"ZILANT_PRIME_PSEUDOHSM"


def _read_file_first_line(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.readline().strip()
    except Exception:
        return ""


def get_device_fingerprint() -> str:
    """Return deterministic short string identifying this device."""
    factors: list[str] = [
        platform.system(),
        platform.machine(),
        platform.processor() or "",
        platform.version(),
        platform.release(),
        os.getenv("HOSTNAME", ""),
        os.getenv("USER", ""),
        str(os.cpu_count() or 0),
        platform.python_version(),
        os.getenv("HOME", ""),
        _read_file_first_line("/etc/machine-id"),
        _read_file_first_line("/proc/cpuinfo"),
    ]
    blob = "|".join(factors).encode()
    digest = hmac.new(_HMAC_KEY, blob, hashlib.sha256).hexdigest()
    return digest[:32]
