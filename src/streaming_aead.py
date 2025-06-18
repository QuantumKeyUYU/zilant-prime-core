"""Streaming AEAD using XChaCha20-Poly1305 with PyNaCl fallback."""

from __future__ import annotations

try:  # pragma: no cover - executed at import time
    from cryptography.hazmat.primitives.ciphers.aead import XChaCha20Poly1305

    def encrypt_chunk(key: bytes, nonce: bytes, data: bytes, aad: bytes = b"") -> bytes:
        """Encrypt a chunk of ``data`` using ``key`` and ``nonce``."""
        return XChaCha20Poly1305(key).encrypt(nonce, data, aad)

    def decrypt_chunk(key: bytes, nonce: bytes, data: bytes, aad: bytes = b"") -> bytes:
        """Decrypt a chunk previously encrypted with :func:`encrypt_chunk`."""
        return XChaCha20Poly1305(key).decrypt(nonce, data, aad)

except Exception:  # pragma: no cover - fallback branch
    from nacl.bindings import crypto_aead_xchacha20poly1305_ietf_decrypt, crypto_aead_xchacha20poly1305_ietf_encrypt

    def encrypt_chunk(key: bytes, nonce: bytes, data: bytes, aad: bytes = b"") -> bytes:
        """Encrypt using PyNaCl bindings."""
        return crypto_aead_xchacha20poly1305_ietf_encrypt(data, aad, nonce, key)

    def decrypt_chunk(key: bytes, nonce: bytes, data: bytes, aad: bytes = b"") -> bytes:
        """Decrypt using PyNaCl bindings."""
        return crypto_aead_xchacha20poly1305_ietf_decrypt(data, aad, nonce, key)
