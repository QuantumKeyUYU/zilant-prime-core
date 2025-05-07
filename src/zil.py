"""
ZIL-контейнер: упаковка / распаковка данных с VDF-защитой
формат v2 (без поля tries)

MAGIC (4) | salt (32) | vdf_iters (4 BE) | proof (32) |
nonce (12) | metadata_len (4 BE) | metadata (…) | ciphertext+tag (…)
"""

import os
import struct
from typing import Tuple

from cryptography.exceptions import InvalidTag

from .kdf import derive_key
from .vdf import generate_vdf, verify_partial_proof
from .aead import encrypt, decrypt

MAGIC = b"ZIL1"            # сигнатура формата
SALT_LEN = 32
NONCE_LEN = 12
PROOF_LEN = 32


# ─────────────────────────── helpers ────────────────────────────
def _pack_uint32(value: int) -> bytes:
    return struct.pack(">I", value)


def _unpack_uint32(buf: bytes, offset: int) -> Tuple[int, int]:
    """Возвращает (значение, новый offset)."""
    return struct.unpack(">I", buf[offset : offset + 4])[0], offset + 4


# ─────────────────────── основной API ───────────────────────────
def create_zil(
    data: bytes,
    passphrase: str,
    vdf_iters: int,
    metadata: bytes = b"",
) -> bytes:
    """
    Упаковать данные в .zil-контейнер.

    :param data:        произвольные данные
    :param passphrase:  пароль (строка)
    :param vdf_iters:   количество итераций HR-VDF
    :param metadata:    необязательные метаданные (байты)
    :return:            байтовый контейнер
    """
    # 1) соль и ключ
    salt = os.urandom(SALT_LEN)
    key = derive_key(passphrase.encode(), salt=salt)

    # 2) VDF-доказательство строим от самой соли
    proof = generate_vdf(salt, vdf_iters)  # 32 байта

    # 3) AEAD-шифрование (proof+metadata → Associated Data)
    nonce, ciphertext = encrypt(key, data, proof + metadata)

    # 4) сборка контейнера
    buf = bytearray()
    buf += MAGIC
    buf += salt
    buf += _pack_uint32(vdf_iters)
    buf += proof
    buf += nonce
    buf += _pack_uint32(len(metadata))
    buf += metadata
    buf += ciphertext
    return bytes(buf)


def unpack_zil(zil_bytes: bytes, passphrase: str) -> Tuple[bytes | None, bytes | None]:
    """
    Распаковать .zil-контейнер.
    Возвращает (plaintext, metadata) либо (None, None) при ошибке проверки.
    """
    try:
        idx = 0

        # ── MAGIC
        if zil_bytes[idx : idx + 4] != MAGIC:
            return None, None
        idx += 4

        # ── salt
        salt = zil_bytes[idx : idx + SALT_LEN]
        idx += SALT_LEN

        # ── vdf_iters
        vdf_iters, idx = _unpack_uint32(zil_bytes, idx)

        # ── proof
        proof = zil_bytes[idx : idx + PROOF_LEN]
        idx += PROOF_LEN

        # ── VDF-проверка
        if not verify_partial_proof(salt, proof, vdf_iters):
            return None, None

        # ── nonce
        nonce = zil_bytes[idx : idx + NONCE_LEN]
        idx += NONCE_LEN

        # ── metadata
        meta_len, idx = _unpack_uint32(zil_bytes, idx)
        metadata = zil_bytes[idx : idx + meta_len]
        idx += meta_len

        # ── ciphertext + tag
        ciphertext = zil_bytes[idx:]

        # ── дешифрование
        key = derive_key(passphrase.encode(), salt=salt)
        plaintext = decrypt(key, nonce, ciphertext, proof + metadata)
        return plaintext, metadata

    except (InvalidTag, Exception):
        # Ошибка пароля, VDF, формата или тегов аутентичности
        return None, None
