import os
import pytest
from zilant_prime_core.crypto.aead import (
    encrypt_aead,
    decrypt_aead,
    generate_nonce,
    DEFAULT_KEY_LENGTH,
    AEADInvalidTagError,
)

KEY = os.urandom(DEFAULT_KEY_LENGTH)
NONCE = generate_nonce()
MSG = b"hi"


def test_bad_key_len():
    with pytest.raises(ValueError):
        encrypt_aead(KEY[:-1], NONCE, MSG)


def test_bad_nonce_len():
    with pytest.raises(ValueError):
        encrypt_aead(KEY, NONCE[:-1], MSG)


def test_invalid_tag():
    ct = encrypt_aead(KEY, NONCE, MSG)
    tampered = bytearray(ct)
    tampered[-1] ^= 1
    with pytest.raises(AEADInvalidTagError):
        decrypt_aead(KEY, NONCE, bytes(tampered))
