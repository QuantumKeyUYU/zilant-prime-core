# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT
"""Simplified Quantum Anonymity Layer (QAL).

This module provides a very small abstraction over ``PQSign`` to mimic
ring signature behaviour. It should **not** be considered a real
implementation of post-quantum ring signatures but merely a helper for
experimentation and tests.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple, cast

from .pq_sign import PQSign


class QAL:
    """Manage a group of post-quantum signers."""

    def __init__(self, group_size: int, work_dir: Path) -> None:
        self.signers: List[PQSign] = []
        self.keys: List[Tuple[Path, Path]] = []
        self.work_dir = work_dir
        self.work_dir.mkdir(parents=True, exist_ok=True)
        for i in range(group_size):
            signer = PQSign()
            priv = work_dir / f"sk_{i}.bin"
            pub = work_dir / f"pk_{i}.bin"
            signer.keygen(priv, pub)
            self.signers.append(signer)
            self.keys.append((priv, pub))

    def sign(self, message: bytes, index: int) -> bytes:
        priv, _ = self.keys[index]
        return cast(bytes, self.signers[index].sign(message, priv))

    def verify(self, message: bytes, signature: bytes) -> bool:
        for signer, (_, pub) in zip(self.signers, self.keys, strict=False):
            if signer.verify(message, signature, pub):
                return True
        return False
