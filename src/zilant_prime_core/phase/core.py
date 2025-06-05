"""Experimental Phase-Entropy key generation and Quantum-Phase encryption."""

from __future__ import annotations

import hashlib
import hmac
import platform
import struct
import time
from dataclasses import dataclass, field

from zilant_prime_core.crypto.aead import (
    AEADInvalidTagError,
    decrypt_aead,
    encrypt_aead,
    generate_nonce,
)
from zilant_prime_core.utils.constants import DEFAULT_KEY_LENGTH, DEFAULT_NONCE_LENGTH


def generate_phase_key(*, length: int = DEFAULT_KEY_LENGTH, rounds: int = 32, jitter_loops: int = 1000) -> bytes:
    """Generate a pseudo-random key using timing jitter."""
    if not isinstance(length, int) or length <= 0:
        raise ValueError("length must be positive int")
    if not isinstance(rounds, int) or rounds <= 0:
        raise ValueError("rounds must be positive int")
    if not isinstance(jitter_loops, int) or jitter_loops <= 0:
        raise ValueError("jitter_loops must be positive int")

    data = bytearray()
    for _ in range(rounds):
        start = time.perf_counter_ns()
        dummy = 0
        for i in range(jitter_loops):
            dummy ^= i
        delta = time.perf_counter_ns() - start
        data.extend(struct.pack("!Q", delta ^ dummy))
    return hashlib.sha256(bytes(data)).digest()[:length]


def hardware_fingerprint() -> bytes:
    """Return a stable fingerprint for the current machine."""
    info = (
        platform.platform(),
        platform.machine(),
        platform.processor(),
    )
    joined = "|".join(filter(None, info)).encode()
    return hashlib.sha256(joined).digest()


@dataclass
class QuantumPhaseCipher:
    """Self-adapting cipher that changes complexity after failures."""

    complexity: int = 32
    _master: bytes = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._master = hmac.new(
            hardware_fingerprint(), generate_phase_key(rounds=self.complexity), hashlib.sha256
        ).digest()

    def _derive_key(self) -> bytes:
        return hmac.new(hardware_fingerprint(), self._master, hashlib.sha256).digest()

    def encrypt(self, data: bytes) -> bytes:
        if not isinstance(data, (bytes, bytearray)):
            raise ValueError("data must be bytes")
        key = self._derive_key()
        nonce = generate_nonce()
        ct = encrypt_aead(key, nonce, data, hardware_fingerprint())
        return nonce + ct

    def decrypt(self, blob: bytes) -> bytes:
        if not isinstance(blob, (bytes, bytearray)) or len(blob) < DEFAULT_NONCE_LENGTH:
            raise ValueError("blob is too short")
        nonce = blob[:DEFAULT_NONCE_LENGTH]
        ct = blob[DEFAULT_NONCE_LENGTH:]
        key = self._derive_key()
        try:
            out = decrypt_aead(key, nonce, ct, hardware_fingerprint())
            self.complexity = 32
            self.__post_init__()
            return out
        except AEADInvalidTagError:
            # escalate complexity on failure
            self.complexity = min(self.complexity * 2, 256)
            self.__post_init__()
            raise
