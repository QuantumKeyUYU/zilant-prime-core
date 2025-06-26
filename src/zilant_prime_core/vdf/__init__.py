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


def posw(seed: bytes, steps: int) -> tuple[bytes, bool]:
    """Compatibility wrapper for property tests.

    Returns a tuple of the proof and ``True`` on success.  ``generate_elc_vdf``
    performs all required validation and will raise ``ValueError`` for invalid
    inputs.
    """

    proof = generate_elc_vdf(seed, steps)
    return proof, True


def check_posw(proof: bytes, seed: bytes, steps: int) -> bool:
    """Compatibility wrapper used by property tests.

    Simply delegates to :func:`verify_elc_vdf` with the argument order expected
    by the older API (``proof, seed, steps``).
    """

    try:
        return verify_elc_vdf(seed, steps, proof)
    except ValueError:
        # Historic behaviour: invalid proofs simply return False rather than
        # raising an exception.
        return False

__all__ = [
    "generate_elc_vdf",
    "verify_elc_vdf",
    "generate_landscape",
    "verify_landscape",
    "VDFVerificationError",
    "posw",
    "check_posw",
]
