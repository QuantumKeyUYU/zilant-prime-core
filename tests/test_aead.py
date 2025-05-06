import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.aead import encrypt, decrypt
import os

def test_encrypt_decrypt():
    key = os.urandom(32)
    plaintext = b"hello world"
    aad = b"context info"

    nonce, ciphertext = encrypt(key, plaintext, aad)
    decrypted = decrypt(key, nonce, ciphertext, aad)

    assert decrypted == plaintext
