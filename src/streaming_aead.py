from typing import Optional, cast

try:
    # Попытка использовать нативную реализацию из cryptography
    from cryptography.hazmat.primitives.ciphers.aead import XChaCha20Poly1305 as _NativeAEAD
except ImportError:
    _NativeAEAD = None  # type: ignore[assignment]


def encrypt_chunk(
    key: bytes,
    nonce: bytes,
    data: bytes,
    aad: Optional[bytes] = None,
) -> bytes:
    """
    Шифрует один кусок данных с помощью XChaCha20-Poly1305.
    Если доступна нативная реализация, используем её, иначе – PyNaCl binding.
    """
    header = aad or b""
    if _NativeAEAD is not None:
        aead = _NativeAEAD(key)
        return cast(bytes, aead.encrypt(nonce, data, header))
    # Падаем на PyNaCl
    from nacl.bindings import crypto_aead_xchacha20poly1305_ietf_encrypt  # type: ignore[import-error]

    return cast(bytes, crypto_aead_xchacha20poly1305_ietf_encrypt(data, header, nonce, key))


def decrypt_chunk(
    key: bytes,
    nonce: bytes,
    ciphertext: bytes,
    aad: Optional[bytes] = None,
) -> bytes:
    """
    Дешифрует один кусок данных, зашифрованный XChaCha20-Poly1305.
    """
    header = aad or b""
    if _NativeAEAD is not None:
        aead = _NativeAEAD(key)
        return cast(bytes, aead.decrypt(nonce, ciphertext, header))
    # Падаем на PyNaCl
    from nacl.bindings import crypto_aead_xchacha20poly1305_ietf_decrypt  # type: ignore[import-error]

    return cast(bytes, crypto_aead_xchacha20poly1305_ietf_decrypt(ciphertext, header, nonce, key))
