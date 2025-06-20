# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT
"""Quantum-Safe Stealth Addresses (QSSA).

This module provides a very small interface for generating one-time
X25519 key pairs and deriving a shared address using HKDF. It is not a
full Monero-style stealth implementation but demonstrates the concept.
"""

from __future__ import annotations

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from typing import Optional, Tuple, cast

from .pq_crypto import HybridKEM


class QSSA:
    """Generate one-time key pairs and shared addresses."""

    def __init__(self) -> None:
        try:
            self.kem: Optional[HybridKEM] = HybridKEM()
        except Exception:  # pragma: no cover - optional dependency
            self.kem = None
        self._private: Optional[x25519.X25519PrivateKey] = None

    def generate_keypair(self) -> Tuple[bytes, bytes]:
        """Return a new X25519 `(public, private)` key pair."""
        priv = x25519.X25519PrivateKey.generate()
        self._private = priv
        pub = priv.public_key()
        pub_bytes = pub.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        priv_bytes = priv.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        )
        return pub_bytes, priv_bytes

    def derive_shared_address(self, their_pub: bytes) -> bytes:
        if self._private is None:
            raise ValueError("generate_keypair must be called first")
        other = x25519.X25519PublicKey.from_public_bytes(their_pub)
        shared = self._private.exchange(other)
        hkdf = HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=b"qssa")
        return cast(bytes, hkdf.derive(shared))
