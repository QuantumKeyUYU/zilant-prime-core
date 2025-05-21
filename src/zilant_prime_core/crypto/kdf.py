# src/zilant_prime_core/crypto/kdf.py

import os
from typing import Union

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.backends import default_backend

from zilant_prime_core.utils.constants import DEFAULT_KEY_LENGTH, DEFAULT_SALT_LENGTH

def generate_salt() -> bytes:
    """
    Генерирует случайную соль DEFAULT_SALT_LENGTH байт.
    """
    return os.urandom(DEFAULT_SALT_LENGTH)

def derive_key(
    password: Union[str, bytes],
    salt: bytes,
    key_length: int = DEFAULT_KEY_LENGTH
) -> bytes:
    """
    Простой PBKDF2-HMAC-SHA256 KDF → key_length байт.
    Из пароля (str/bytes) и соли в DEFAULT_SALT_LENGTH байт выдаёт ключ длины key_length.
    """
    if isinstance(password, str):
        password = password.encode("utf-8")
    if not isinstance(password, (bytes, bytearray)):
        raise ValueError("Password must be bytes or string.")
    if not isinstance(salt, (bytes, bytearray)) or len(salt) != DEFAULT_SALT_LENGTH:
        raise ValueError(f"Salt must be {DEFAULT_SALT_LENGTH} bytes.")
    if not isinstance(key_length, int) or key_length <= 0:
        raise ValueError("Key length must be a positive integer.")

    kdf = PBKDF2HMAC(
        algorithm=SHA256(),
        length=key_length,
        salt=salt,
        iterations=100_000,
        backend=default_backend()
    )
    return kdf.derive(password)

def derive_key_dynamic(
    password: Union[str, bytes],
    salt: bytes,
    profile: float,
    key_length: int = DEFAULT_KEY_LENGTH,
    time_max: int = 5,
    mem_min: int = 32 * 1024,
    mem_max: int = 128 * 1024,
) -> bytes:
    """
    Динамический KDF: пока просто оборачиваем derive_key (PBKDF2).
    Параметры time_max, mem_min, mem_max и profile игнорируются.
    """
    # Валидация совместимая с derive_key
    return derive_key(password, salt, key_length)
