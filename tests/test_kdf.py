import os
from src.kdf import derive_key

def test_derive_key():
    key, salt = derive_key("pass")
    assert isinstance(key, bytes) and len(key) == 32
    assert isinstance(salt, bytes) and len(salt) == 32
