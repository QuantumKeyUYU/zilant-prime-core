# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

__all__ = [
    "from_b64",
    "from_hex",
    "to_b64",
    "to_hex",
]

"""Hex / Base64 helpers (Ruff & mypy clean)."""

import base64
import binascii


def to_hex(data: bytes) -> str:
    """Bytes → hex-строка (ASCII)."""
    return data.hex()


def from_hex(text: str) -> bytes:
    """Hex-строка (ASCII) → bytes."""
    try:
        return bytes.fromhex(text)
    except ValueError as exc:
        raise ValueError("Invalid hex") from exc


def to_b64(data: bytes) -> str:
    """Bytes → Base64-строка (ASCII)."""
    return base64.b64encode(data).decode("ascii")


def from_b64(text: str) -> bytes:
    """Base64-строка (ASCII) → bytes."""
    try:
        return base64.b64decode(text, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("Invalid base64") from exc
