# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core Contributors
"""Post-quantum cryptography helpers."""

from __future__ import annotations

import abc
from typing import Tuple

try:
    import oqs
except Exception:  # pragma: no cover - optional dependency
    oqs = None

try:
    from pqclean import dilithium2, kyber768
except Exception:  # pragma: no cover - optional dependency
    kyber768 = None
    dilithium2 = None

from kdf import derive_key


class KEM(abc.ABC):
    """Abstract interface for key encapsulation mechanisms."""

    @abc.abstractmethod
    def generate_keypair(self) -> Tuple[bytes, bytes]:
        """Return ``(public_key, private_key)``."""

    @abc.abstractmethod
    def encapsulate(self, public_key: bytes) -> Tuple[bytes, bytes]:
        """Encapsulate ``public_key`` and return ``(ciphertext, shared_secret)``."""

    @abc.abstractmethod
    def decapsulate(self, private_key: bytes, ciphertext: bytes) -> bytes:
        """Decapsulate ``ciphertext`` using ``private_key`` and return ``shared_secret``."""


class SignatureScheme(abc.ABC):
    """Abstract interface for digital signature schemes."""

    @abc.abstractmethod
    def generate_keypair(self) -> Tuple[bytes, bytes]:
        """Return ``(public_key, private_key)``."""

    @abc.abstractmethod
    def sign(self, private_key: bytes, message: bytes) -> bytes:
        """Return signature for ``message``."""

    @abc.abstractmethod
    def verify(self, public_key: bytes, message: bytes, signature: bytes) -> bool:
        """Verify ``signature`` for ``message``."""


class Kyber768KEM(KEM):
    """Kyber768 KEM implementation via ``pqclean``."""

    def __init__(self) -> None:
        if kyber768 is None:
            raise RuntimeError("pqclean.kyber768 not installed")

    def generate_keypair(self) -> Tuple[bytes, bytes]:
        pk, sk = kyber768.generate_keypair()
        return pk, sk

    def encapsulate(self, public_key: bytes) -> Tuple[bytes, bytes]:
        ct, ss = kyber768.encapsulate(public_key)
        return ct, ss

    def decapsulate(self, private_key: bytes, ciphertext: bytes) -> bytes:
        return kyber768.decapsulate(ciphertext, private_key)

    @staticmethod
    def ciphertext_length() -> int:
        return getattr(kyber768, "CIPHERTEXT_SIZE", len(kyber768.encapsulate(kyber768.generate_keypair()[0])[0]))


class Dilithium2Signature(SignatureScheme):
    """Dilithium2 signature scheme via ``pqclean``."""

    def __init__(self) -> None:
        if dilithium2 is None:
            raise RuntimeError("pqclean.dilithium2 not installed")

    def generate_keypair(self) -> Tuple[bytes, bytes]:
        pk, sk = dilithium2.generate_keypair()
        return pk, sk

    def sign(self, private_key: bytes, message: bytes) -> bytes:
        return dilithium2.sign(message, private_key)

    def verify(self, public_key: bytes, message: bytes, signature: bytes) -> bool:
        try:
            return dilithium2.verify(message, signature, public_key)
        except Exception:
            return False


class OQSKyberKEM(KEM):
    """Kyber768 KEM via ``liboqs`` if available."""

    def __init__(self) -> None:
        if oqs is None:
            raise RuntimeError("liboqs not installed")
        self._kem = oqs.KeyEncapsulation("Kyber768")

    def generate_keypair(self) -> Tuple[bytes, bytes]:
        return self._kem.generate_keypair()

    def encapsulate(self, public_key: bytes) -> Tuple[bytes, bytes]:
        return self._kem.encapsulate(public_key)

    def decapsulate(self, private_key: bytes, ciphertext: bytes) -> bytes:
        return self._kem.decapsulate(ciphertext, private_key)

    def ciphertext_length(self) -> int:
        return self._kem.details.length_ciphertext


def derive_key_pq(shared_secret: bytes, length: int = 32) -> bytes:
    """Derive a symmetric key from a KEM shared secret."""

    if not isinstance(shared_secret, (bytes, bytearray)):
        raise TypeError("shared_secret must be bytes or bytearray")

    key = derive_key(bytes(shared_secret), b"pq_salt")
    return key[:length]
