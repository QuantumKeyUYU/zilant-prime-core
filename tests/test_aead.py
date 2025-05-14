# tests/test_aead.py
import pytest
import os
import hashlib # For potential future use or consistency
import builtins # Ensure builtins is imported if debug_print is used

# Function to ensure printing works during tests if default print doesn't
def debug_print(*args, **kwargs):
    """A simple print function that might work better in test environments."""
    builtins.print("DEBUG:", *args, **kwargs)


# Import the correct exceptions defined in aead.py
# ПОЖАЛУЙСТА, УБЕДИТЕСЬ, ЧТО ВАША СТРОКА ИМПОРТА ИСКЛЮЧЕНИЙ ВЫГЛЯДИТ ИМЕННО ТАК:
from zilant_prime_core.crypto.aead import (
    encrypt_aead,
    decrypt_aead,
    generate_nonce,
    AEADError, # <-- Импортируем это
    AEADInvalidTagError, # <-- Импортируем это
    DEFAULT_NONCE_LENGTH,
    DEFAULT_KEY_LENGTH
)

# Helper function to generate a key (using a simple hash for tests)
# In a real scenario, this would come from KDF.
def generate_test_key(password: bytes, salt: bytes) -> bytes:
    """Generates a test key (simple hash)."""
    hashed = hashlib.sha256(password + salt).digest()
    return hashed[:DEFAULT_KEY_LENGTH] # Truncate or extend to required key length

# Basic encryption and decryption test
def test_encrypt_decrypt_success():
    key = os.urandom(DEFAULT_KEY_LENGTH)
    nonce = generate_nonce()
    payload = b"This is the secret message."
    aad = b"additional authenticated data"

    ciphertext_with_tag = encrypt_aead(key, nonce, payload, aad)
    assert isinstance(ciphertext_with_tag, bytes)
    # Ciphertext length is payload length + tag length (16 bytes for GCM)
    assert len(ciphertext_with_tag) == len(payload) + 16

    decrypted_payload = decrypt_aead(key, nonce, ciphertext_with_tag, aad)
    assert decrypted_payload == payload

# Test with empty payload
def test_encrypt_decrypt_empty_payload():
    key = os.urandom(DEFAULT_KEY_LENGTH)
    nonce = generate_nonce()
    payload = b""
    aad = b"some aad"

    ciphertext_with_tag = encrypt_aead(key, nonce, payload, aad)
    assert isinstance(ciphertext_with_tag, bytes)
    assert len(ciphertext_with_tag) == 16 # Only the tag

    decrypted_payload = decrypt_aead(key, nonce, ciphertext_with_tag, aad)
    assert decrypted_payload == payload

# Test with empty AAD
def test_encrypt_decrypt_empty_aad():
    key = os.urandom(DEFAULT_KEY_LENGTH)
    nonce = generate_nonce()
    payload = b"Payload without AAD."
    aad = b""

    ciphertext_with_tag = encrypt_aead(key, nonce, payload, aad)
    assert isinstance(ciphertext_with_tag, bytes)
    assert len(ciphertext_with_tag) == len(payload) + 16

    decrypted_payload = decrypt_aead(key, nonce, ciphertext_with_tag, aad)
    assert decrypted_payload == payload

# Test with invalid key
def test_decrypt_invalid_key():
    key = os.urandom(DEFAULT_KEY_LENGTH)
    wrong_key = os.urandom(DEFAULT_KEY_LENGTH)
    nonce = generate_nonce()
    payload = b"Secret data."
    aad = b"aad data"

    ciphertext_with_tag = encrypt_aead(key, nonce, payload, aad)

    # Decrypting with a wrong key should result in InvalidTagError
    with pytest.raises(AEADInvalidTagError):
        decrypt_aead(wrong_key, nonce, ciphertext_with_tag, aad)

# Test with invalid nonce
def test_decrypt_invalid_nonce():
    key = os.urandom(DEFAULT_KEY_LENGTH)
    nonce = generate_nonce()
    wrong_nonce = generate_nonce()
    payload = b"Secret data."
    aad = b"aad data"

    ciphertext_with_tag = encrypt_aead(key, nonce, payload, aad)

    # Decrypting with a wrong nonce should result in InvalidTagError
    with pytest.raises(AEADInvalidTagError):
        decrypt_aead(key, wrong_nonce, ciphertext_with_tag, aad)

# Test with tampered ciphertext
def test_decrypt_tampered_ciphertext():
    key = os.urandom(DEFAULT_KEY_LENGTH)
    nonce = generate_nonce()
    payload = b"Secret data."
    aad = b"aad data"

    ciphertext_with_tag = encrypt_aead(key, nonce, payload, aad)
    tampered_ciphertext_with_tag = bytearray(ciphertext_with_tag)
    # Tamper with the first byte of the ciphertext (before the tag)
    tampered_ciphertext_with_tag[0] ^= 0xFF

    # Decrypting with tampered ciphertext should result in InvalidTagError
    with pytest.raises(AEADInvalidTagError):
        decrypt_aead(key, nonce, bytes(tampered_ciphertext_with_tag), aad)

# Test with tampered tag
def test_decrypt_tampered_tag():
    key = os.urandom(DEFAULT_KEY_LENGTH)
    nonce = generate_nonce()
    payload = b"Secret data."
    aad = b"aad data"

    ciphertext_with_tag = encrypt_aead(key, nonce, payload, aad)
    tampered_ciphertext_with_tag = bytearray(ciphertext_with_tag)
    # Tamper with the first byte of the tag (last 16 bytes)
    tampered_ciphertext_with_tag[-16] ^= 0xFF

    # Decrypting with tampered tag should result in InvalidTagError
    with pytest.raises(AEADInvalidTagError):
        decrypt_aead(key, nonce, bytes(tampered_ciphertext_with_tag), aad)

# Test with tampered AAD
def test_decrypt_tampered_aad():
    key = os.urandom(DEFAULT_KEY_LENGTH)
    nonce = generate_nonce()
    payload = b"Secret data."
    aad = b"additional authenticated data"
    tampered_aad = b"different additional authenticated data"


    ciphertext_with_tag = encrypt_aead(key, nonce, payload, aad)

    # Decrypting with tampered AAD should result in InvalidTagError
    with pytest.raises(AEADInvalidTagError):
        decrypt_aead(key, nonce, ciphertext_with_tag, tampered_aad)

# Test invalid input lengths for encrypt_aead
def test_encrypt_aead_invalid_input_lengths():
    key = os.urandom(DEFAULT_KEY_LENGTH)
    nonce = generate_nonce()
    payload = b"data"
    aad = b"aad"

    # Invalid key length
    with pytest.raises(ValueError, match=f"Key must be {DEFAULT_KEY_LENGTH} bytes long."):
        encrypt_aead(key[:DEFAULT_KEY_LENGTH - 1], nonce, payload, aad)

    # Invalid nonce length
    with pytest.raises(ValueError, match=f"Nonce must be {DEFAULT_NONCE_LENGTH} bytes long."):
        encrypt_aead(key, nonce[:DEFAULT_NONCE_LENGTH - 1], payload, aad)

# Test invalid input lengths for decrypt_aead
def test_decrypt_aead_invalid_input_lengths():
    key = os.urandom(DEFAULT_KEY_LENGTH)
    nonce = generate_nonce()
    payload = b"data"
    aad = b"aad"
    ciphertext_with_tag = encrypt_aead(key, nonce, payload, aad)

    # Invalid key length
    with pytest.raises(ValueError, match=f"Key must be {DEFAULT_KEY_LENGTH} bytes long."):
        decrypt_aead(key[:DEFAULT_KEY_LENGTH - 1], nonce, ciphertext_with_tag, aad)

    # Invalid nonce length
    with pytest.raises(ValueError, match=f"Nonce must be {DEFAULT_NONCE_LENGTH} bytes long."):
        decrypt_aead(key, nonce[:DEFAULT_NONCE_LENGTH - 1], ciphertext_with_tag, aad)

    # Ciphertext too short for tag
    with pytest.raises(ValueError, match="Ciphertext is too short to contain the authentication tag."):
         decrypt_aead(key, nonce, b"short", aad)