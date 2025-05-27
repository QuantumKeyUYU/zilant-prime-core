# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

__all__ = [
    "from_b64",
    "from_hex",
    "to_b64",
    "to_hex",
]

# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT
"""Hex / Base64 helpers (Ruff & mypy clean)."""

import base64
import binascii
"""
Разбор / вывод часто-используемых текстовых представлений байт-строк.

* hex ↔ bytes
* base64url ↔ bytes
"""

from __future__ import annotations

import base64
import binascii

__all__ = ["to_hex", "from_hex", "to_b64", "from_b64"]


def to_hex(data: bytes) -> str:
    return data.hex()


def from_hex(text: str) -> bytes:
    try:
        return bytes.fromhex(text)
    except ValueError as exc:
        raise ValueError("Invalid hex") from exc
def from_hex(hex_str: str) -> bytes:
    try:
        return bytes.fromhex(hex_str)
    except ValueError as exc:  # pragma: no cover
        raise ValueError("invalid hex") from exc


def to_b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode()


def from_b64(text: str) -> bytes:
    try:
        return base64.b64decode(text, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("Invalid base64") from exc
def from_b64(b64_str: str) -> bytes:
    try:
        return base64.urlsafe_b64decode(b64_str.encode())
    except (binascii.Error, ValueError) as exc:  # pragma: no cover
        raise ValueError("invalid base64") from exc
    