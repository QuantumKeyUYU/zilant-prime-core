import hashlib
import hmac

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

_storage: dict[int, bytes] = {}
_next_handle = 1


def _store(key: bytes) -> int:
    global _next_handle
    handle = _next_handle
    _next_handle += 1
    _storage[handle] = key
    return handle


def derive_sk0_from_fp(fp: bytes) -> int:
    hkdf = HKDF(algorithm=hashes.SHA256(), length=32, salt=b"sk0_salt", info=b"SK0")
    sk0 = hkdf.derive(fp)
    return _store(sk0)


def derive_sk1(sk0_handle: int, user_secret: bytes) -> int:
    sk0 = _storage.get(sk0_handle)
    if sk0 is None:
        raise ValueError("invalid handle")
    salt = hmac.new(sk0, user_secret, hashlib.sha256).digest()
    hkdf = HKDF(algorithm=hashes.SHA256(), length=32, salt=salt, info=b"SK1")
    sk1 = hkdf.derive(sk0)
    return _store(sk1)


def get_sk_from_handle(handle: int) -> bytes:
    return _storage[handle]


def release_sk(handle: int) -> None:
    _storage.pop(handle, None)
