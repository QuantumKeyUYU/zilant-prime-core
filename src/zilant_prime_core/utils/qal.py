# src/zilant_prime_core/utils/qal.py
# SPDX-FileCopyrightText: 2025 Zilant Prime Core Contributors
# SPDX-License-Identifier: MIT
"""Simplified Quantum Anonymity Layer (QAL).

This module provides a very small abstraction over ``PQSign`` to mimic
ring signature behaviour. It should **not** be considered a real
implementation of post-quantum ring signatures but merely a helper for
experimentation and tests.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import List, Tuple

from .pq_sign import PQSign


class QAL:
    """Manage a group of post-quantum signers."""

    def __init__(self, group_size: int, work_dir: Path) -> None:
        self.signers: List[PQSign] = []
        self.work_dir = work_dir
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.key_file = self.work_dir / "keys.json"
        keys: List[Tuple[str, str]] = []
        for i in range(group_size):
            signer = PQSign()
            priv = work_dir / f"sk_{i}.bin"
            pub = work_dir / f"pk_{i}.bin"
            signer.keygen(priv, pub)
            self.signers.append(signer)
            keys.append((str(priv), str(pub)))
        self.key_file.write_text(json.dumps(keys))
        self.keys = [(Path(priv), Path(pub)) for priv, pub in keys]

    def sign(self, message: bytes, index: int) -> bytes:
        priv, _ = self.keys[index]
        result: bytes = self.signers[index].sign(message, priv)
        return result

    def verify(self, message: bytes, signature: bytes, pubkeys: List[bytes]) -> bool:
        """Verify the signature against a list of public‐key bytes."""
        for signer, pub_bytes in zip(self.signers, pubkeys, strict=False):
            # Use TemporaryDirectory for auto-cleanup of any temp files
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_pub = Path(tmpdir) / "pubkey.bin"
                tmp_pub.write_bytes(pub_bytes)
                if signer.verify(message, signature, tmp_pub):
                    return True
        return False
