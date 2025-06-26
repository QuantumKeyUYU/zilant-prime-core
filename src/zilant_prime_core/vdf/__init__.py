# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

# src/zilant_prime_core/vdf/__init__.py

from .phase_vdf import (
    VDFVerificationError,
    generate_elc_vdf,
    generate_landscape,
    verify_elc_vdf,
    verify_landscape,
)
from .vdf import generate_posw_sha256, verify_posw_sha256


def posw(seed: bytes, steps: int) -> tuple[bytes, bool]:
    """Return POSW proof and success flag."""
    proof = generate_posw_sha256(seed, steps)
    return proof, True


def check_posw(proof: bytes, seed: bytes, steps: int) -> bool:
    """Check the given POSW proof."""
    return verify_posw_sha256(seed, proof, steps)


__all__ = [
    "generate_elc_vdf",
    "verify_elc_vdf",
    "generate_landscape",
    "verify_landscape",
    "posw",
    "check_posw",
    "VDFVerificationError",
]
