import os
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

def encrypt(key: bytes, plaintext: bytes, associated_data: bytes = b'') -> tuple[bytes, bytes]:
    """
    Шифрует ChaCha20-Poly1305, возвращает (nonce, ciphertext).
    """
    aead = ChaCha20Poly1305(key)
    nonce = os.urandom(12)
    ct = aead.encrypt(nonce, plaintext, associated_data)
    return nonce, ct

def decrypt(key: bytes, nonce: bytes, ciphertext: bytes, associated_data: bytes = b'') -> bytes:
    """
    Расшифровывает ChaCha20-Poly1305, кидает InvalidTag при неверном ключе/AD.
    """
    aead = ChaCha20Poly1305(key)
    return aead.decrypt(nonce, ciphertext, associated_data)
