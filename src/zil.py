"""
ZIL‑контейнер v3.1 (ONE_SHOT + TLV‑metadata)
"""
from __future__ import annotations

import os
import struct
from typing import Dict, Tuple

from cryptography.exceptions import InvalidTag

from aead import decrypt, encrypt
from kdf import derive_key
from tlv import decode_tlv, encode_tlv
from vdf import generate_vdf, verify_partial_proof

MAGIC = b"ZIL1"
FLAG_ONE_SHOT = 0x01
SALT_LEN, NONCE_LEN, PROOF_LEN = 32, 12, 32
_consumed: set[bytes] = set()


def _u32(x: int) -> bytes:
    return struct.pack(">I", x)


def _get_u32(buf: bytes, i: int) -> Tuple[int, int]:
    return struct.unpack(">I", buf[i : i + 4])[0], i + 4


def create_zil(
    data: bytes,
    passphrase: str,
    vdf_iters: int,
    *,
    metadata: Dict[int, bytes] | None = None,
    one_shot: bool = False,
) -> bytes:
    salt = os.urandom(SALT_LEN)
    key = derive_key(passphrase.encode(), salt=salt)
    proof = generate_vdf(salt, vdf_iters)
    tlv = encode_tlv(metadata or {})
    nonce, ct = encrypt(key, data, proof + tlv)

    flags = FLAG_ONE_SHOT if one_shot else 0
    buf = bytearray()
    buf += MAGIC + bytes([flags]) + salt + _u32(vdf_iters) + proof + nonce
    buf += _u32(len(tlv)) + tlv + ct
    return bytes(buf)


def unpack_zil(zil: bytes, passphrase: str) -> Tuple[bytes | None, Dict[int, bytes] | None]:
    try:
        idx = 0
        if zil[idx : idx + 4] != MAGIC:
            return None, None
        idx += 4

        flags = zil[idx]
        idx += 1
        one_shot = bool(flags & FLAG_ONE_SHOT)

        salt = zil[idx : idx + SALT_LEN]
        idx += SALT_LEN
        vdf_iters, idx = _get_u32(zil, idx)
        proof = zil[idx : idx + PROOF_LEN]
        idx += PROOF_LEN

        if one_shot and proof in _consumed:
            return None, None
        if not verify_partial_proof(salt, proof, vdf_iters):
            return None, None

        nonce = zil[idx : idx + NONCE_LEN]
        idx += NONCE_LEN
        meta_len, idx = _get_u32(zil, idx)
        tlv = zil[idx : idx + meta_len]
        idx += meta_len
        ct = zil[idx:]

        key = derive_key(passphrase.encode(), salt=salt)
        pt = decrypt(key, nonce, ct, proof + tlv)

        if one_shot:
            _consumed.add(proof)

        return pt, decode_tlv(tlv)
    except (InvalidTag, Exception):
        return None, None
