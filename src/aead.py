import os

from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305


def encrypt(
    key: bytes, plaintext: bytes, aad: bytes, nonce: bytes = None
) -> (bytes, bytes):
    """
    AEAD ChaCha20-Poly1305 encrypt.
    :param key:       32-байтный ключ
    :param plaintext: данные
    :param aad:       дополнительные данные (здесь всегда b'')
    :param nonce:     12-байтный nonce; если None — генерируется случайно
    :returns:         (nonce, ciphertext||tag)
    """
    if nonce is None:
        nonce = os.urandom(12)
    aead = ChaCha20Poly1305(key)
    ct = aead.encrypt(nonce, plaintext, aad)
    return nonce, ct


def decrypt(key: bytes, nonce: bytes, ciphertext: bytes, aad: bytes) -> bytes:
    """
    AEAD ChaCha20-Poly1305 decrypt.
    :param key:        32-байтный ключ
    :param nonce:      12-байтный nonce
    :param ciphertext: зашифрованные данные + tag
    :param aad:        дополнительные данные (здесь всегда b'')
    :returns:          plaintext
    """
    aead = ChaCha20Poly1305(key)
    return aead.decrypt(nonce, ciphertext, aad)
