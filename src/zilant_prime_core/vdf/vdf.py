# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

import hashlib
from typing import Tuple

__all__ = [
    "VDFVerificationError",
    "generate_posw_sha256",
    "prove_posw_sha256",
    "verify_posw_sha256",
    "posw",
    "check_posw",
]


class VDFVerificationError(Exception):
    """Общая ошибка Proof-of-Sequential-Work."""

    pass


def generate_posw_sha256(data: bytes, steps: int = 1) -> bytes:
    """
    Proof-of-Sequential-Work с SHA-256.
    По умолчанию steps=1, но можно задать любое положительное целое.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise ValueError("Seed must be bytes.")
    if not isinstance(steps, int) or steps <= 0:
        raise ValueError("Steps must be a positive integer.")
    h = data
    for _ in range(steps):
        h = hashlib.sha256(h).digest()
    return h


# для совместимости с остальным API
prove_posw_sha256 = generate_posw_sha256


def verify_posw_sha256(data: bytes, proof: bytes, steps: int = 1) -> bool:
    """
    Проверяет, что generate_posw_sha256(data, steps) == proof.
    По умолчанию steps=1.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise ValueError("Seed must be bytes.")
    if not isinstance(steps, int) or steps <= 0:
        raise ValueError("Steps must be a positive integer.")
    # некорректное proof (не bytes или неправильный размер) считаем ложью
    if not isinstance(proof, (bytes, bytearray)) or len(proof) != hashlib.sha256(b"").digest_size:
        return False
    h = data
    for _ in range(steps):
        h = hashlib.sha256(h).digest()
    return h == proof


def posw(data: bytes, steps: int = 1) -> Tuple[bytes, bool]:
    """
    Упрощённый интерфейс для тестов:
    возвращает (proof, True) или кидает ValueError при некорректных аргументах.
    """
    proof = generate_posw_sha256(data, steps)
    return proof, True


def check_posw(proof: bytes, data: bytes, steps: int = 1) -> bool:
    """
    Интерфейс для тестов: check_posw(proof, data, steps).
    """
    if not isinstance(proof, (bytes, bytearray)):
        return False
    expected = generate_posw_sha256(data, steps)
    if len(proof) != len(expected):
        return False
    return proof == expected
