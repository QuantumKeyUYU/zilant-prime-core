# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT
"""Secure Remote Attestation placeholder using PQ signatures."""

from __future__ import annotations

from pathlib import Path

from .pq_sign import PQSign


class QuantumRA:
    """Attest and verify device information."""

    def __init__(self, work_dir: Path) -> None:
        self.signer = PQSign()
        self.work_dir = work_dir
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.sk = work_dir / "ra_sk.bin"
        self.pk = work_dir / "ra_pk.bin"
        self.signer.keygen(self.sk, self.pk)

    def attest(self, info: bytes) -> bytes:
        return self.signer.sign(info, self.sk)

    def verify(self, info: bytes, signature: bytes) -> bool:
        return self.signer.verify(info, signature, self.pk)
