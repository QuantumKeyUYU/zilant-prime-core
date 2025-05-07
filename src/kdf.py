import os
from argon2.low_level import hash_secret_raw, Type

def derive_key(passphrase: str) -> tuple[bytes, bytes]:
    salt = os.urandom(32)
    key = hash_secret_raw(
        secret=passphrase.encode("utf-8"),
        salt=salt,
        time_cost=3,
        memory_cost=64 * 1024,
        parallelism=1,
        hash_len=32,
        type=Type.ID
    )
    return key, salt
