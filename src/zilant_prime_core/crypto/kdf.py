# src/zilant_prime_core/crypto/kdf.py

import os
from typing import Union

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from zilant_prime_core.utils.constants import (
    DEFAULT_KEY_LENGTH,
    DEFAULT_SALT_LENGTH,
)

# from zilant_prime_core.crypto.g_new import G_new  # <-- для будущей динамики

# Параметры для совместимости с динамическим KDF (в текущей реализации игнорируются)
DEFAULT_MEMORY_MIN = 2**15  # 32 MiB
DEFAULT_MEMORY_MAX = 2**17  # 128 MiB
DEFAULT_TIME_MAX = 5  # до 5 итераций


def generate_salt() -> bytes:
    """
    Генерирует случайную соль длины DEFAULT_SALT_LENGTH байт.
    """
    return os.urandom(DEFAULT_SALT_LENGTH)


def derive_key(
    password: Union[str, bytes],
    salt: bytes,
    key_length: int = DEFAULT_KEY_LENGTH,
) -> bytes:
    """
    Статичный PBKDF2-HMAC-SHA256 KDF → key_length байт.
    Из пароля (str/bytes) и соли (DEFAULT_SALT_LENGTH байт) выдаёт ключ длины key_length.
    """
    if isinstance(password, str):
        password = password.encode("utf-8")
    if not isinstance(password, (bytes, bytearray)):
        raise ValueError("Password must be bytes or string.")
    if not isinstance(salt, (bytes, bytearray)):
        raise ValueError("Salt must be bytes.")
    if len(salt) != DEFAULT_SALT_LENGTH:
        raise ValueError(f"Salt must be {DEFAULT_SALT_LENGTH} bytes long.")
    if not isinstance(key_length, int) or key_length <= 0:
        raise ValueError("Key length must be a positive integer.")

    kdf = PBKDF2HMAC(
        algorithm=SHA256(),
        length=key_length,
        salt=salt,
        iterations=100_000,
        backend=default_backend(),
    )
    return kdf.derive(password)


def derive_key_dynamic(
    password: Union[str, bytes],
    salt: bytes,
    profile: float,
    key_length: int = DEFAULT_KEY_LENGTH,
    time_max: int = DEFAULT_TIME_MAX,
    mem_min: int = DEFAULT_MEMORY_MIN,
    mem_max: int = DEFAULT_MEMORY_MAX,
) -> bytes:
    """
    "Динамический" KDF: сигнатура для будущего расширения.
    Сейчас возвращает результат derive_key и не использует профиль.
    """
    if not isinstance(profile, (int, float)):
        raise ValueError("Profile must be a number.")
    # Остальные проверки в derive_key

    # Можно реализовать динамику через G_new(profile), если потребуется.
    return derive_key(password, salt, key_length)
