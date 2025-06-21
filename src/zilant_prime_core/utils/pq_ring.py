# SPDX-License-Identifier: MIT
"""Лёгкая обёртка над OQS/Ed25519 для кольцевых подписей."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Tuple, cast

try:  # основная ветка – liboqs
    from oqs import Signature  # type: ignore

    _HAS_OQS = True  # pragma: no cover
except Exception:  # fallback – Ed25519 (PyNaCl)
    from nacl import signing  # type: ignore

    _HAS_OQS = False

KeyPair = Tuple[bytes, bytes]  # (pub, priv)


class PQRing:
    """Мини-реализация кольцевых подписей.

    * alg        – строка-код для liboqs или «Ed25519» в fallback-режиме
    * group_size – число участников в кольце
    * work_dir   – куда сохранять ring_keys.json
    """

    # ------------------------------------------------------------------ #
    def __init__(self, alg: str, group_size: int, work_dir: Path) -> None:
        self.alg = alg
        self.work_dir = work_dir
        self.work_dir.mkdir(parents=True, exist_ok=True)

        self.signers = []
        self.keys: List[KeyPair] = []

        for _ in range(group_size):
            if _HAS_OQS:
                sig = Signature(alg)  # type: ignore[abstract]
                pub, priv = sig.generate_keypair()
                self.signers.append(sig)
            else:
                sk = signing.SigningKey.generate()  # type: ignore[attr-defined]
                self.signers.append(sk)
                pub = sk.verify_key.encode()
                priv = sk.encode()  # type: ignore[attr-defined]

            self.keys.append((pub, priv))

        self._save_keys()

    # ------------------------------------------------------------------ #
    def _save_keys(self) -> None:
        path = self.work_dir / "ring_keys.json"
        path.write_text(json.dumps([{"pub": p.hex(), "priv": s.hex()} for p, s in self.keys]))

    # ------------------------------------------------------------------ #
    def sign(self, msg: bytes, signer_index: int = 0) -> bytes:
        """Подписывает *msg* участником с индексом *signer_index*."""
        pub, priv = self.keys[signer_index]
        signer = self.signers[signer_index]

        if _HAS_OQS:
            return cast(bytes, signer.sign(msg, priv))  # type: ignore[arg-type]

        sk = signer  # SigningKey
        return cast(bytes, sk.sign(msg).signature)  # type: ignore[attr-defined]

    # ------------------------------------------------------------------ #
    def verify(self, msg: bytes, sig: bytes) -> bool:
        """Проверяет подпись – пройдёт, если она валидна хотя бы под одним ключом."""
        for pub, _ in self.keys:
            if _HAS_OQS:
                v = Signature(self.alg)  # type: ignore[abstract]
                if v.verify(msg, sig, pub):  # pragma: no cover – зависит от oqs
                    return True
            else:
                vk = signing.VerifyKey(pub)  # type: ignore[attr-defined]
                try:
                    vk.verify(msg, sig)
                    return True
                except Exception:
                    continue
        return False
