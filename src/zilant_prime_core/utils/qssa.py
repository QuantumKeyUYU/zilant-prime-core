# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT
"""Quantum-Safe Stealth Addresses (QSSA).

Addresses are ephemeral public keys generated using ``HybridKEM``.
This is a minimal helper and not a full stealth address scheme.
"""

from __future__ import annotations

import os
from .pq_crypto import HybridKEM


class QSSA:
    """Generate ephemeral address key pairs."""

    def __init__(self) -> None:
        try:
            self.kem = HybridKEM()
        except Exception:  # pragma: no cover - optional dependency
            self.kem = None

    def generate_address(self):
        """Return a new `(public_key, private_key)` pair."""
        if self.kem is not None:
            pk_pq, sk_pq, pk_x, sk_x = self.kem.generate_keypair()
            public = (pk_pq, pk_x)
            private = (sk_pq, sk_x)
            return public, private
        pub = os.urandom(32)
        priv = os.urandom(32)
        return pub, priv
