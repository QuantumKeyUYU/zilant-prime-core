# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core Contributors
"""Branchless cryptographic primitives."""

from __future__ import annotations

import argon2.low_level as a2
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

__all__ = [
    "encrypt_chacha20_poly1305",
    "decrypt_chacha20_poly1305",
    "derive_key_argon2id",
]


def encrypt_chacha20_poly1305(key: bytes, nonce: bytes, data: bytes) -> bytes:
    """Encrypt *data* with ChaCha20-Poly1305."""
    ch = ChaCha20Poly1305(bytes(key))
    return ch.encrypt(bytes(nonce), data, None)


def decrypt_chacha20_poly1305(key: bytes, nonce: bytes, data: bytes) -> bytes:
    """Decrypt ChaCha20-Poly1305 payload."""
    ch = ChaCha20Poly1305(bytes(key))
    return ch.decrypt(bytes(nonce), data, None)


def derive_key_argon2id(
    password: bytes,
    salt: bytes,
    mem_cost: int = 512 * 1024,
    time_cost: int = 4,
) -> bytes:
    """Derive key via Argon2id."""
    pwd = bytes(password)
    sl = bytes(salt)
    return a2.hash_secret_raw(
        secret=pwd,
        salt=sl,
        time_cost=time_cost,
        memory_cost=mem_cost,
        parallelism=1,
        hash_len=32,
        type=a2.Type.ID,
    )
