# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

"""Collects hardware factors and computes a device fingerprint."""

from __future__ import annotations

import hashlib
import hmac
import platform
import socket
import uuid
from pathlib import Path
from typing import List

SALT32 = b"ZILANT_PSEUDOHSM_SALT0123456789012"  # 32 bytes


def _get_factors() -> List[bytes]:
    factors: List[bytes] = []
    try:
        factors.append(platform.processor().encode())
    except Exception:
        factors.append(b"proc")
    try:
        factors.append(platform.node().encode())
    except Exception:
        factors.append(b"node")
    try:
        with open("/etc/machine-id", "rb") as f:
            factors.append(f.read().strip())
    except Exception:
        factors.append(uuid.getnode().to_bytes(6, "big"))
    try:
        factors.append(socket.gethostname().encode())
    except Exception:
        factors.append(b"\x00" * 6)
    # additional fillers
    for path in [
        "/sys/devices/virtual/dmi/id/product_uuid",
        "/sys/devices/virtual/dmi/id/board_serial",
        "/sys/devices/virtual/dmi/id/product_serial",
    ]:
        try:
            factors.append(Path(path).read_bytes().strip())
        except Exception:
            factors.append(b"\x00" * 8)
    # ensure at least 12 factors
    while len(factors) < 12:
        factors.append(b"\x00" * 8)
    return factors[:12]


def get_device_fp() -> bytes:
    """Returns HMAC(SALT32, factor) for each factor concatenated."""
    out = bytearray()
    for factor in _get_factors():
        out.extend(hmac.new(SALT32, factor, hashlib.sha256).digest())
    return bytes(out)
