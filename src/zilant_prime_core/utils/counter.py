# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

"""Monotonic counter storage."""

from __future__ import annotations

import hashlib
import hmac
import os
import struct
from pathlib import Path
from typing import Optional, Tuple

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from .crypto_wrapper import get_sk_bytes

_COUNTER_FILE = Path.home() / ".zilant" / ".hidden_counter"
_current_sk1_handle: Optional[int] = None


def set_sk1_handle(handle: int) -> None:
    global _current_sk1_handle
    _current_sk1_handle = handle


def _sk1_bytes() -> bytes:
    if _current_sk1_handle is None:
        raise RuntimeError("SK1 handle not set")
    return get_sk_bytes(_current_sk1_handle)


def read_file_counter() -> Tuple[Optional[int], Optional[bytes], Optional[bytes]]:
    try:
        data = _COUNTER_FILE.read_bytes()
        if len(data) != 8 + 32 + 64:
            return None, None, None
        counter = struct.unpack(">Q", data[:8])[0]
        hmac_val = data[8:40]
        sig = data[40:104]
        return counter, hmac_val, sig
    except FileNotFoundError:
        return None, None, None


def write_file_counter(val: int, sk1_handle: int) -> None:
    sk1 = get_sk_bytes(sk1_handle)
    _COUNTER_FILE.parent.mkdir(parents=True, exist_ok=True)
    counter_bytes = struct.pack(">Q", val)
    hmac_val = hmac.new(sk1, counter_bytes, hashlib.sha256).digest()
    priv = Ed25519PrivateKey.from_private_bytes(sk1)
    sig = priv.sign(counter_bytes)
    with open(_COUNTER_FILE, "wb") as f:
        f.write(counter_bytes + hmac_val + sig)


def get_monotonic_counter() -> int:
    val, hmac_val, sig = read_file_counter()
    if val is None or hmac_val is None or sig is None:
        return 0
    sk1 = _sk1_bytes()
    expected_hmac = hmac.new(sk1, struct.pack(">Q", val), hashlib.sha256).digest()
    if hmac_val != expected_hmac:
        return 0
    try:
        Ed25519PrivateKey.from_private_bytes(sk1).public_key().verify(sig, struct.pack(">Q", val))
    except InvalidSignature:
        return 0
    return val


def increment_monotonic_counter(sk1_handle: int) -> int:
    current = get_monotonic_counter()
    new_val = current + 1
    write_file_counter(new_val, sk1_handle)
    return new_val


def init_counter_storage(sk1_handle: int) -> None:
    if get_monotonic_counter() == 0:
        write_file_counter(0, sk1_handle)


def verify_no_rollback(current_counter: int, stored_nonce: int) -> bool:
    return current_counter >= 0 and ((int(os.path.getmtime(str(_COUNTER_FILE))) + 299) // 300) >= stored_nonce
