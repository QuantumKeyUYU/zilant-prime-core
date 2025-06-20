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
import json

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
        return cast(bytes, self.signers[index].sign(message, priv))

    def verify(self, message: bytes, signature: bytes, pubkeys: List[bytes]) -> bool:
        for signer, pub_bytes in zip(self.signers, pubkeys, strict=False):
            pub_path = Path("/tmp") / "_tmp_pk.bin"
            pub_path.write_bytes(pub_bytes)
            if signer.verify(message, signature, pub_path):
                return True
        return False
