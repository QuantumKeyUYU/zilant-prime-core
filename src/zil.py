"""
ZIL‑контейнер v3.1
Структура:

MAGIC(4) | FLAGS(1) | SALT(32) | VDF_ITERS(4 BE) | PROOF(32) |
NONCE(12) | META_LEN(4 BE) | META_TLV(...) | CIPHERTEXT+TAG(...)

FLAGS:
 bit0 (0x01) = ONE_SHOT   — контейнер можно вскрыть ровно один раз
 bit1‑7                 — зарезервированы
"""

from __future__ import annotations

import os
import struct
from typing import Dict, Tuple

from cryptography.exceptions import InvalidTag

from .aead import decrypt, encrypt
from .kdf import derive_key
from .tlv import decode_tlv, encode_tlv
from .vdf import generate_vdf, verify_partial_proof

# ─────────── константы ───────────
MAGIC = b"ZIL1"
FLAG_ONE_SHOT = 0b0000_0001

SALT_LEN = 32
NONCE_LEN = 12
PROOF_LEN = 32

_consumed: set[bytes] = set()  # proof‑ы уже вскрытых ONE_SHOT контейнеров


# ─────────── маленькие утилиты ───────────
def _u32(value: int) -> bytes:
    return struct.pack(">I", value)


def _get_u32(buf: bytes, idx: int) -> Tuple[int, int]:
    return struct.unpack(">I", buf[idx : idx + 4])[0], idx + 4


# ─────────── публичный API ───────────
def create_zil(
    data: bytes,
    passphrase: str,
    vdf_iters: int,
    *,
    metadata: Dict[int, bytes] | None = None,
    one_shot: bool = False,
) -> bytes:
    """
    Упаковать данные в ZIL‑контейнер.

    :param data:        произвольные данные
    :param passphrase:  строковый пароль
    :param vdf_iters:   количество итераций HR‑VDF
    :param metadata:    TLV‑словарь {type:int -> bytes}
    :param one_shot:    True = контейнер можно вскрыть только один раз
    :return:            байтовый контейнер
    """
    # 1) соль + ключ (Argon2id)
    salt = os.urandom(SALT_LEN)
    key = derive_key(passphrase.encode(), salt=salt)

    # 2) HR‑VDF‑доказательство (seed = salt)
    proof = generate_vdf(salt, vdf_iters)

    # 3) TLV‑метаданные
    tlv_bytes = encode_tlv(metadata or {})

    # 4) AEAD (ChaCha20‑Poly1305)
    ad = proof + tlv_bytes
    nonce, ciphertext = encrypt(key, data, ad)

    # 5) сборка контейнера
    flags = FLAG_ONE_SHOT if one_shot else 0
    buf = bytearray()
    buf += MAGIC
    buf += bytes([flags])
    buf += salt
    buf += _u32(vdf_iters)
    buf += proof
    buf += nonce
    buf += _u32(len(tlv_bytes))
    buf += tlv_bytes
    buf += ciphertext
    return bytes(buf)


def unpack_zil(
    zil_bytes: bytes,
    passphrase: str,
) -> Tuple[bytes | None, Dict[int, bytes] | None]:
    """
    Распаковать ZIL‑контейнер.
    :return: (plaintext, metadata_dict) либо (None, None) при любой ошибке
    """
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

        # блокируем повторное вскрытие ONE_SHOT
        if one_shot and proof in _consumed:
            return None, None

        # HR‑VDF проверка
        if not verify_partial_proof(salt, proof, vdf_iters):
            return None, None

        # NONCE
        nonce = zil_bytes[idx : idx + NONCE_LEN]
        idx += NONCE_LEN

        # META TLV
        meta_len, idx = _get_u32(zil_bytes, idx)
        tlv_bytes = zil_bytes[idx : idx + meta_len]
        idx += meta_len
        metadata = decode_tlv(tlv_bytes)

        # CIPHERTEXT + TAG
        ciphertext = zil_bytes[idx:]

        # расшифровка
        key = derive_key(passphrase.encode(), salt=salt)
        plaintext = decrypt(key, nonce, ciphertext, proof + tlv_bytes)

        # отмечаем вскрытый ONE_SHOT
        if one_shot:
            _consumed.add(proof)

        return plaintext, metadata

    except (InvalidTag, Exception):
        # любая ошибка = (None, None)
        return None, None
