import os
import hashlib
from typing import Tuple

def derive_key(passphrase: str, salt: bytes = None) -> Tuple[bytes, bytes]:
    """
    Derives a 32-byte key from the given passphrase using PBKDF2-HMAC-SHA256.
    Returns (key, salt). If salt is not provided, a new 32-byte salt is generated.
    """
    if salt is None:
        salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac(
        'sha256',
        passphrase.encode('utf-8'),
        salt,
        390_000,   # число итераций — современный рекомендованный минимум
        dklen=32
    )
    return key, salt
