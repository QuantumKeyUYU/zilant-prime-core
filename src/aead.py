import os
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

def encrypt(key: bytes, data: bytes, aad: bytes = b"") -> tuple[bytes, bytes]:
    """
    Возвращает (nonce:12B, ciphertext+tag).
    """
    nonce = os.urandom(12)
    aead = ChaCha20Poly1305(key)
    ct = aead.encrypt(nonce, data, aad)
    return nonce, ct

def decrypt(key: bytes, nonce: bytes, ct: bytes, aad: bytes = b"") -> bytes:
    """
    Расшифровка ChaCha20-Poly1305.
    """
    aead = ChaCha20Poly1305(key)
    return aead.decrypt(nonce, ct, aad)
