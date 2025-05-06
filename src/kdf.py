from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
from cryptography.hazmat.backends import default_backend
import os


def derive_key(passphrase: str) -> tuple[bytes, bytes]:
    salt = os.urandom(32)
    kdf = Argon2id(
        memory_cost=65536,
        time_cost=4,
        parallelism=1,
        length=32,
        salt=salt,
        backend=default_backend()
    )
    key = kdf.derive(passphrase.encode())
    return key, salt
