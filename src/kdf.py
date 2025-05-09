import os
from argon2.low_level import (
    hash_secret_raw, Type
)

DEFAULT_TIME_COST = 3
DEFAULT_MEMORY_COST = 65536  # 64 MiB
DEFAULT_PARALLELISM = 4
DEFAULT_SALT_LENGTH = 32
KEY_LENGTH = 32

def derive_key(password: bytes, 
               salt: bytes = None, 
               time_cost: int = DEFAULT_TIME_COST, 
               mem_cost: int = DEFAULT_MEMORY_COST, 
               parallelism: int = DEFAULT_PARALLELISM) -> bytes:
    """
    Derives a cryptographic key using Argon2id.
    
    :param password: User-provided password.
    :param salt: Optional salt; randomly generated if None.
    :param time_cost: Iteration count.
    :param mem_cost: Memory cost in kibibytes.
    :param parallelism: Degree of parallelism.
    :return: Derived 32-byte key.
    """
    if salt is None:
        salt = os.urandom(DEFAULT_SALT_LENGTH)
    elif len(salt) != DEFAULT_SALT_LENGTH:
        raise ValueError(f"Salt must be {DEFAULT_SALT_LENGTH} bytes long")

    # Validate parameters
    if not (1 <= time_cost <= 10):
        raise ValueError("time_cost must be between 1 and 10")
    if not (8192 <= mem_cost <= 1048576):
        raise ValueError("mem_cost must be between 8192 (8 MiB) and 1048576 (1 GiB)")
    if not (1 <= parallelism <= 16):
        raise ValueError("parallelism must be between 1 and 16")

    key = hash_secret_raw(
        secret=password,
        salt=salt,
        time_cost=time_cost,
        memory_cost=mem_cost,
        parallelism=parallelism,
        hash_len=KEY_LENGTH,
        type=Type.ID
    )
    
    return key
