import pytest

from aead import decrypt, encrypt


def test_aead_roundtrip():
    key = b"\x00" * 32
    plaintext = b"hello world"
    aad = b"associated data"

    # Encrypt returns (nonce, ciphertext_with_tag)
    nonce, ciphertext = encrypt(key, plaintext, aad)

    # Nonce must be 12 bytes
    assert isinstance(nonce, bytes)
    assert len(nonce) == 12

    # Ciphertext should be bytes and at least as long as plaintext + tag
    assert isinstance(ciphertext, bytes)
    assert len(ciphertext) >= len(plaintext)

    # Decrypt with the same AAD yields original plaintext
    decrypted = decrypt(key, nonce, ciphertext, aad)
    assert decrypted == plaintext


def test_aead_wrong_aad_fails():
    key = b"\x00" * 32
    plaintext = b"secret message"
    aad = b"good aad"
    bad_aad = b"bad aad"

    nonce, ciphertext = encrypt(key, plaintext, aad)

    # Decrypting with wrong AAD should raise an exception
    with pytest.raises(Exception):
        decrypt(key, nonce, ciphertext, bad_aad)
