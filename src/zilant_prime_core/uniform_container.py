# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core Contributors
"""Uniform-size encrypted container."""

from __future__ import annotations

import json
import os
from typing import Tuple

from .crypto_core import decrypt_chacha20_poly1305, encrypt_chacha20_poly1305

__all__ = ["pack", "unpack"]

_PAD = 4096


def _pad(data: bytes) -> bytes:
    rem = (-len(data)) % _PAD
    return data + b"\x00" * rem


def pack(metadata: dict, payload: bytes, key: bytes) -> bytes:
    meta = json.dumps(metadata).encode()
    plain = len(meta).to_bytes(4, "big") + meta + payload
    blob = _pad(plain)
    nonce = os.urandom(12)
    ct = encrypt_chacha20_poly1305(key, nonce, blob)
    return nonce + ct


def unpack(blob: bytes, key: bytes) -> Tuple[dict, bytes]:
    nonce = blob[:12]
    ct = blob[12:]
    plain = decrypt_chacha20_poly1305(key, nonce, ct)
    meta_len = int.from_bytes(plain[:4], "big")
    meta_json = plain[4 : 4 + meta_len]
    payload = plain[4 + meta_len :].rstrip(b"\x00")
    return json.loads(meta_json.decode()), payload
