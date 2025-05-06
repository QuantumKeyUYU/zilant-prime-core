import os
import time
import struct
import hashlib

from src.vdf import vdf
from src.aead import encrypt, decrypt
from cryptography.exceptions import InvalidTag

MAGIC = b"ZIL1"
VERSION = 1

def create_zil(plaintext: bytes,
               key: bytes,
               vdf_iters: int,
               tries: int = 3,
               metadata: bytes = b"") -> bytes:
    """
    Упаковать данные в .zil-контейнер:
    [magic(4) | version(1) | tries(1) | vdf_iters(4) | timestamp(8)
     | salt(32) | nonce(12) | watermark(16) | ciphertext+tag ]
    """
    salt = os.urandom(32)
    nonce, ciphertext = encrypt(key, plaintext, metadata)

    # VDF на salt
    vstate = vdf(salt, vdf_iters)
    # Phase fingerprint
    F = hashlib.sha256(vstate + key + metadata).digest()
    watermark = F[:16]

    timestamp = int(time.time())

    header = struct.pack(
        ">4s B B I Q 32s 12s 16s",
        MAGIC,
        VERSION,
        tries,
        vdf_iters,
        timestamp,
        salt,
        nonce,
        watermark
    )
    return header + ciphertext


def unpack_zil(container: bytes, key: bytes, metadata: bytes = b""):
    """
    Попытаться распаковать .zil-контейнер.
    - Если ключ верный → возвращает (plaintext, None)
    - Если ключ неверный → возвращает (None, new_container_bytes) (tries--, zero-feedback)
    - Если попыток не осталось → возвращает (None, None) (self-destruct)
    """
    # Разбор заголовка
    fmt = ">4s B B I Q 32s 12s 16s"
    header_size = struct.calcsize(fmt)
    magic, version, tries, vdf_iters, timestamp, salt, nonce, watermark = \
        struct.unpack(fmt, container[:header_size])
    ciphertext = container[header_size:]

    # Проверки формата
    if magic != MAGIC or version != VERSION:
        return None, None

    # Выполняем VDF и проверяем watermark
    vstate = vdf(salt, vdf_iters)
    expected_F = hashlib.sha256(vstate + key + metadata).digest()[:16]
    # Убираем одну попытку
    tries -= 1

    # Если watermark совпал — правильный ключ
    if expected_F == watermark:
        try:
            plaintext = decrypt(key, nonce, ciphertext, metadata)
            return plaintext, None
        except InvalidTag:
            # На случай, если AEAD провалит аутентификацию
            pass

    # Неправильный ключ или ошибка → zero-feedback, self-destruct при tries<=0
    if tries <= 0:
        return None, None

    # Собираем новый контейнер с декрементом tries
    new_header = struct.pack(
        ">4s B B I Q 32s 12s 16s",
        MAGIC, VERSION, tries, vdf_iters, timestamp, salt, nonce, watermark
    )
    return None, new_header + ciphertext
