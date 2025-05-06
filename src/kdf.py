# src/kdf.py

import os
from argon2 import PasswordHasher
from argon2.low_level import Type, hash_secret_raw

def derive_key(passphrase: str, salt: bytes = None) -> (bytes, bytes):
    """
    Генерирует 256-битный ключ из passphrase и salt.
    Если salt не передан, генерирует 32 random bytes.
    Возвращает (key, salt).
    """
    if salt is None:
        salt = os.urandom(32)
    # Параметры: time_cost=3, memory_cost=64 MiB, parallelism=1
    key = hash_secret_raw(
        secret=passphrase.encode('utf-8'),
        salt=salt,
        time_cost=3,
        memory_cost=64 * 1024,
        parallelism=1,
        hash_len=32,
        type=Type.ID,
    )
    return key, salt
