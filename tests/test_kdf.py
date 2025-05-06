# tests/test_kdf.py

import pytest
from src.kdf import derive_key

def test_derive_key_output_length():
    key, salt = derive_key("my secret")
    assert isinstance(salt, bytes) and len(salt) == 32
    assert isinstance(key, bytes) and len(key) == 32

def test_same_passphrase_and_salt_produces_same_key():
    salt = b'\x00' * 32
    k1, _ = derive_key("password", salt)
    k2, _ = derive_key("password", salt)
    assert k1 == k2

def test_different_salt_changes_key():
    k1, _ = derive_key("password")
    k2, _ = derive_key("password")
    assert k1 != k2
