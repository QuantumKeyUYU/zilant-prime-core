# tests/test_aead_extra.py

import pytest
from zilant_prime_core.crypto.aead import (
    decrypt_aead,
    generate_nonce,
    DEFAULT_NONCE_LENGTH,
    DEFAULT_KEY_LENGTH,
)


def test_decrypt_short_ciphertext():
    key = b"\x00" * DEFAULT_KEY_LENGTH
    nonce = b"\x00" * DEFAULT_NONCE_LENGTH
    # ciphertext too short to contain a tag → ValueError
    with pytest.raises(ValueError):
        decrypt_aead(key, nonce, b"", aad=b"")


def test_generate_nonce_length():
    n = generate_nonce()
    assert isinstance(n, bytes)
    assert len(n) == DEFAULT_NONCE_LENGTH
