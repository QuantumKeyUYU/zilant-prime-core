# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

"""Shard generation and loading via pseudo-HSM."""

from __future__ import annotations

import hashlib
import hmac
import os
import struct
import time
import uuid
from typing import NamedTuple

from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

from .counter import get_monotonic_counter, increment_monotonic_counter
from .crypto_wrapper import get_sk_bytes
from .device_fp import get_device_fp
from .logging import self_destruct_all


class DecryptedShard(NamedTuple):
    shard_key: bytes
    shard_id: uuid.UUID
    usage_counter: int
    wallclock_nonce: int


def _sk1_bytes(handle: int) -> bytes:
    return get_sk_bytes(handle)


def generate_shard(sk1_handle: int) -> bytes:
    shard_key = os.urandom(32)
    shard_id = uuid.uuid4()
    usage_counter = get_monotonic_counter()
    wallclock_nonce = (int(time.time()) + 299) // 300
    sk1 = _sk1_bytes(sk1_handle)
    hmac_fp_shard = hmac.new(sk1, shard_id.bytes + get_device_fp(), hashlib.sha256).digest()
    plaintext = (
        shard_id.bytes
        + struct.pack(">Q", usage_counter)
        + struct.pack(">Q", wallclock_nonce)
        + hmac_fp_shard
        + shard_key
    )
    key_shard = hmac.new(sk1, b"shard", hashlib.sha256).digest()
    nonce = os.urandom(12)
    ciphertext = ChaCha20Poly1305(key_shard).encrypt(nonce, plaintext, None)
    return nonce + ciphertext


def load_shard(sk1_handle: int, encrypted_shard: bytes) -> DecryptedShard:
    nonce = encrypted_shard[:12]
    ciphertext = encrypted_shard[12:]
    sk1 = _sk1_bytes(sk1_handle)
    key_shard = hmac.new(sk1, b"shard", hashlib.sha256).digest()
    plaintext = ChaCha20Poly1305(key_shard).decrypt(nonce, ciphertext, None)
    shard_id = uuid.UUID(bytes=plaintext[:16])
    usage_counter = struct.unpack(">Q", plaintext[16:24])[0]
    wallclock_nonce = struct.unpack(">Q", plaintext[24:32])[0]
    hmac_fp_shard = plaintext[32:64]
    shard_key = plaintext[64:96]

    expected_hmac = hmac.new(sk1, shard_id.bytes + get_device_fp(), hashlib.sha256).digest()
    if expected_hmac != hmac_fp_shard:
        raise ValueError("FP mismatch")
    current = get_monotonic_counter()
    if usage_counter != current:
        raise ValueError("counter mismatch")
    new_counter = increment_monotonic_counter(sk1_handle)
    return DecryptedShard(shard_key, shard_id, new_counter, wallclock_nonce)


def self_destruct_shard() -> None:
    self_destruct_all()
