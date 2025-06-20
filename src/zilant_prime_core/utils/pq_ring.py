# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT
"""Post-Quantum Ring Signatures using liboqs if available."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List, Tuple, cast

try:
    from oqs import Signature

    _HAS_OQS = True
except Exception:  # pragma: no cover - optional dependency
    from nacl import signing

    _HAS_OQS = False


class PQRing:
    """Manage a group of post-quantum signers for ring signatures."""

    def __init__(self, alg: str, group_size: int, work_dir: Path) -> None:
        self.alg = alg
        self.signers: List[Any] = []
        self.work_dir = work_dir
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.keys: List[Tuple[bytes, bytes]] = []
        for _ in range(group_size):
            if _HAS_OQS:
                signer = Signature(alg)
                pub, priv = signer.generate_keypair()
            else:  # Ed25519 fallback
                signer = signing.SigningKey.generate()
                pub = signer.verify_key.encode()
                priv = signer.encode()
            self.signers.append(signer)
            self.keys.append((pub, priv))
        self._save_keys()

    # ------------------------------------------------------------------
    def _save_keys(self) -> None:
        keys_path = self.work_dir / "ring_keys.json"
        keys_serialized = [{"pub": pub.hex(), "priv": priv.hex()} for pub, priv in self.keys]
        keys_path.write_text(json.dumps(keys_serialized))

    # ------------------------------------------------------------------
    def sign(self, message: bytes, signer_index: int) -> bytes:
        _, priv = self.keys[signer_index]
        signer = self.signers[signer_index]
        if _HAS_OQS:
            return cast(bytes, signer.sign(message, priv))
        sk = signing.SigningKey(priv)
        return cast(bytes, sk.sign(message).signature)

    # ------------------------------------------------------------------
    def verify(self, message: bytes, signature: bytes) -> bool:
        for pub, _ in self.keys:
            if _HAS_OQS:
                verifier = Signature(self.alg)
                if verifier.verify(message, signature, pub):
                    return True
            else:
                vk = signing.VerifyKey(pub)
                try:
                    vk.verify(message, signature)
                    return True
                except Exception:
                    continue
        return False
