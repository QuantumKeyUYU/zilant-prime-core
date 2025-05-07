"""
ZIL-контейнер v3
MAGIC(4) | FLAGS(1) | SALT(32) | VDF_ITERS(4) | PROOF(32) |
NONCE(12) | META_LEN(4) | META | CIPHERTEXT+TAG
"""

import os
import struct
from typing import Tuple

from cryptography.exceptions import InvalidTag

from .kdf import derive_key
from .vdf import generate_vdf, verify_partial_proof
from .aead import encrypt, decrypt

# ─────────────────────────── константы ───────────────────────────
MAGIC = b"ZIL1"
FLAG_ONE_SHOT = 0b0000_0001

SALT_LEN = 32
NONCE_LEN = 12
PROOF_LEN = 32

_consumed: set[bytes] = set()  # proof-ы уже вскрытых one-shot контейнеров


# ─────────────────────────── helpers ─────────────────────────────
def _u32(num: int) -> bytes:
    return struct.pack(">I", num)


def _get_u32(buf: bytes, idx: int) -> Tuple[int, int]:
    return struct.unpack(">I", buf[idx : idx + 4])[0], idx + 4


# ─────────────────────────── API ─────────────────────────────────
def create_zil(
    data: bytes,
    passphrase: str,
    vdf_iters: int,
    *,
    metadata: bytes = b"",
    one_shot: bool = False,
) -> bytes:
    """Упаковать данные в ZIL-v3 контейнер."""
    # ключ
    salt = os.urandom(SALT_LEN)
    key = derive_key(passphrase.encode(), salt=salt)

    # VDF-доказательство (от соли)
    proof = generate_vdf(salt, vdf_iters)

    # AEAD
    nonce, ciphertext = encrypt(key, data, proof + metadata)

    flags = FLAG_ONE_SHOT if one_shot else 0

    buf = bytearray()
    buf += MAGIC
    buf += bytes([flags])
    buf += salt
    buf += _u32(vdf_iters)
    buf += proof
    buf += nonce
    buf += _u32(len(metadata))
    buf += metadata
    buf += ciphertext
    return bytes(buf)


def unpack_zil(
    zil_bytes: bytes,
    passphrase: str,
) -> Tuple[bytes | None, bytes | None]:
    """Распаковать контейнер. Для one-shot возвращает None при повторном вскрытии."""
    try:
        idx = 0

        # MAGIC
        if zil_bytes[idx : idx + 4] != MAGIC:
            return None, None
        idx += 4

        # FLAGS
        flags = zil_bytes[idx]
        idx += 1
        one_shot = bool(flags & FLAG_ONE_SHOT)

        # SALT
        salt = zil_bytes[idx : idx + SALT_LEN]
        idx += SALT_LEN

        # VDF_ITERS
        vdf_iters, idx = _get_u32(zil_bytes, idx)

        # PROOF
        proof = zil_bytes[idx : idx + PROOF_LEN]
        idx += PROOF_LEN

        # one-shot: проверяем повторное вскрытие
        if one_shot and proof in _consumed:
            return None, None

        # VDF verify
        if not verify_partial_proof(salt, proof, vdf_iters):
            return None, None

        # NONCE
        nonce = zil_bytes[idx : idx + NONCE_LEN]
        idx += NONCE_LEN

        # METADATA
        meta_len, idx = _get_u32(zil_bytes, idx)
        metadata = zil_bytes[idx : idx + meta_len]
        idx += meta_len

        ciphertext = zil_bytes[idx:]

        key = derive_key(passphrase.encode(), salt=salt)
        plaintext = decrypt(key, nonce, ciphertext, proof + metadata)

        # mark consumed
        if one_shot:
            _consumed.add(proof)

        return plaintext, metadata

    except (InvalidTag, Exception):
        return None, None
