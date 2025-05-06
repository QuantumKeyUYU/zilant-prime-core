import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.kdf import derive_key


def test_derive_key_returns_key_and_salt():
    key, salt = derive_key("test passphrase")
    assert isinstance(key, bytes)
    assert isinstance(salt, bytes)
    assert len(key) == 32
    assert len(salt) == 32
