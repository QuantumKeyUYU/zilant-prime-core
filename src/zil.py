# src/zil.py
import os
import time
import struct
import hashlib
from src.kdf import derive_key
from src.vdf import vdf
from src.aead import encrypt, decrypt
from cryptography.exceptions import InvalidTag

MAGIC   = b"ZIL1"
VERSION = 1

def create_zil(plaintext: bytes,
               passphrase: str,
               vdf_iters: int = 100000,
               tries: int = 3,
               metadata: bytes = b"") -> bytes:
    # 1) ключ и соль KDF
    key, salt_kdf = derive_key(passphrase)

    # 2) AEAD шифрование
    nonce, ciphertext = encrypt(key, plaintext, metadata)

    # 3) VDF на salt
    vstate = vdf(salt_kdf, vdf_iters)
    watermark = hashlib.sha256(vstate + key + metadata).digest()[:16]

    timestamp = int(time.time())

    # 4) собираем заголовок (4+1+1+4+8+32+12+16 = 78 байт)
    fmt = ">4s B B I Q 32s 12s 16s"
    header = struct.pack(
        fmt,
        MAGIC,
        VERSION,
        tries,
        vdf_iters,
        timestamp,
        salt_kdf,
        nonce,
        watermark
    )
    return header + ciphertext

def unpack_zil(container: bytes,
               passphrase: str,
               metadata: bytes = b""):
    fmt = ">4s B B I Q 32s 12s 16s"
    header_size = struct.calcsize(fmt)

    # разбираем заголовок
    magic, version, tries_left, vdf_iters, timestamp, salt_kdf, nonce, watermark = \
        struct.unpack(fmt, container[:header_size])
    ciphertext = container[header_size:]

    if magic != MAGIC or version != VERSION:
        return None, None

    # деривация того же ключа
    key, _ = derive_key(passphrase, salt=salt_kdf)

    # проверка VDF + watermark
    vstate = vdf(salt_kdf, vdf_iters)
    expected = hashlib.sha256(vstate + key + metadata).digest()[:16]

    # декремент попыток
    tries_left -= 1

    # если ключ верный → пробуем расшифровать
    if expected == watermark:
        try:
            pt = decrypt(key, nonce, ciphertext, metadata)
            return pt, None
        except InvalidTag:
            pass

    # если попыток не осталось → self-destruct
    if tries_left <= 0:
        return None, None

    # иначе возвращаем новый контейнер с уменьшенным tries_left
    new_header = struct.pack(
        fmt,
        MAGIC, VERSION, tries_left, vdf_iters,
        timestamp, salt_kdf, nonce, watermark
    )
    return None, new_header + ciphertext
