# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core Contributors

from __future__ import annotations

import os
from typing import Tuple

from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

from zilant_prime_core.utils.pq_crypto import Kyber768KEM, derive_key_pq

__all__ = ["encrypt", "decrypt", "PQAEAD"]


def encrypt(key: bytes, plaintext: bytes, aad: bytes = b"") -> Tuple[bytes, bytes]:
    """Encrypt ``plaintext`` with ChaCha20-Poly1305 and return ``(nonce, ciphertext)``."""
    if not isinstance(key, (bytes, bytearray)):
        raise TypeError("key must be bytes")
    if len(key) != 32:
        raise ValueError("key must be 32 bytes long")
    nonce = os.urandom(12)
    ch = ChaCha20Poly1305(key)
    ct = ch.encrypt(nonce, plaintext, aad)
    return nonce, ct


def decrypt(key: bytes, nonce: bytes, ciphertext: bytes, aad: bytes = b"") -> bytes:
    """Decrypt ChaCha20-Poly1305 ciphertext produced by :func:`encrypt`."""
    if not isinstance(key, (bytes, bytearray)) or len(key) != 32:
        raise ValueError("key must be 32 bytes long")
    if not isinstance(nonce, (bytes, bytearray)) or len(nonce) != 12:
        raise ValueError("nonce must be 12 bytes long")
    ch = ChaCha20Poly1305(key)
    return ch.decrypt(nonce, ciphertext, aad)


class PQAEAD:
    """Hybrid PQ AEAD using Kyber768 KEM and ChaCha20-Poly1305."""

    _NONCE_LEN = 12

    @staticmethod
    def encrypt(public_key: bytes, plaintext: bytes, aad: bytes = b"") -> bytes:
        kem = Kyber768KEM()
        ct_kem, shared = kem.encapsulate(public_key)
        key = derive_key_pq(shared)
        nonce = os.urandom(PQAEAD._NONCE_LEN)
        ch = ChaCha20Poly1305(key)
        ct = ch.encrypt(nonce, plaintext, aad)
        return ct_kem + nonce + ct

    @staticmethod
    def decrypt(private_key: bytes, payload: bytes, aad: bytes = b"") -> bytes:
        kem = Kyber768KEM()
        ct_len = kem.ciphertext_length()
        kem_ct = payload[:ct_len]
        nonce = payload[ct_len : ct_len + PQAEAD._NONCE_LEN]
        ct = payload[ct_len + PQAEAD._NONCE_LEN :]
        shared = kem.decapsulate(private_key, kem_ct)
        key = derive_key_pq(shared)
        ch = ChaCha20Poly1305(key)
        return ch.decrypt(nonce, ct, aad)
