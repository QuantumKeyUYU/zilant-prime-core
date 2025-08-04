# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

# src/zilant_prime_core/vdf/__init__.py

from .phase_vdf import VDFVerificationError as PhaseVDFError
from .phase_vdf import generate_elc_vdf, generate_landscape, verify_elc_vdf, verify_landscape
from .vdf import VDFVerificationError, check_posw, generate_posw_sha256, posw, prove_posw_sha256, verify_posw_sha256

__all__ = [
    # ELC-VDF
    "PhaseVDFError",
    "generate_elc_vdf",
    "verify_elc_vdf",
    "generate_landscape",
    "verify_landscape",
    # SHA-256 PoSW
    "VDFVerificationError",
    "generate_posw_sha256",
    "prove_posw_sha256",
    "verify_posw_sha256",
    "posw",
    "check_posw",
]
