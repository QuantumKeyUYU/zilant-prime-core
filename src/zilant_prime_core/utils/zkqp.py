# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT
"""Zero-Knowledge Quantum-Proofs (ZKQP) placeholder."""

from __future__ import annotations

import hashlib
from pathlib import Path

from .pq_sign import PQSign


class ZKQP:
    """Very small commitment scheme using ``PQSign``."""

    def __init__(self, work_dir: Path) -> None:
        self.signer = PQSign()
        self.work_dir = work_dir
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.sk = work_dir / "zkqp_sk.bin"
        self.pk = work_dir / "zkqp_pk.bin"
        self.signer.keygen(self.sk, self.pk)

    def prove(self, data: bytes) -> tuple[bytes, bytes]:
        commit = hashlib.sha256(data).digest()
        proof = self.signer.sign(commit, self.sk)
        return commit, proof

    def verify(self, data: bytes, commit: bytes, proof: bytes) -> bool:
        expected = hashlib.sha256(data).digest()
        if commit != expected:
            return False
        return self.signer.verify(commit, proof, self.pk)
