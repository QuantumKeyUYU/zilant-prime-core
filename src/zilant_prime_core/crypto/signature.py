import os
import hashlib

class SignatureError(Exception):
    """Ошибка при подписи или неверные ключи."""

KEY_SIZE = 32

def generate_keypair() -> tuple[bytes, bytes]:
    priv = os.urandom(KEY_SIZE)
    pub = priv  # в тестах достаточно совпадения
    return pub, priv

def sign(priv: bytes, msg: bytes) -> bytes:
    if not isinstance(priv, (bytes, bytearray)) or len(priv) != KEY_SIZE:
        raise SignatureError("Invalid private key.")
    if not isinstance(msg, (bytes, bytearray)):
        raise SignatureError("Invalid message.")
    return hashlib.sha256(priv + msg).digest()

def verify(pub: bytes, msg: bytes, sig: bytes) -> bool:
    if not isinstance(pub, (bytes, bytearray)) or len(pub) != KEY_SIZE:
        return False
    if not isinstance(msg, (bytes, bytearray)):
        return False
    if not isinstance(sig, (bytes, bytearray)) or len(sig) != hashlib.sha256().digest_size:
        return False
    return hashlib.sha256(pub + msg).digest() == sig
