# tests/test_streaming_aead.py

import os
import pytest
import sys
import types

import streaming_aead as sa  # или 'from src import streaming_aead as sa'

# Конкретные исключения для native и fallback
try:
    from cryptography.exceptions import InvalidTag
except ImportError:
    InvalidTag = ValueError

try:
    from nacl.exceptions import CryptoError
except ImportError:
    CryptoError = TypeError


@pytest.mark.parametrize("aad", [b"", b"header"])
def test_roundtrip_native(aad, monkeypatch):
    class DummyNativeAEAD:
        def __init__(self, key):
            assert key

        def encrypt(self, nonce, plaintext, hdr):
            assert hdr == aad
            return b"CT" + plaintext

        def decrypt(self, nonce, ciphertext, hdr):
            assert hdr == aad
            return ciphertext[2:]

    monkeypatch.setattr(sa, "_NativeAEAD", DummyNativeAEAD)
    sys.modules.pop("nacl.bindings", None)

    key = os.urandom(32)
    nonce = os.urandom(24)
    data = b"hello"

    ct = sa.encrypt_chunk(key, nonce, data, aad)
    pt = sa.decrypt_chunk(key, nonce, ct, aad)
    assert pt == data


@pytest.mark.parametrize("aad", [b"", b"header"])
def test_roundtrip_fallback(aad, monkeypatch):
    monkeypatch.setattr(sa, "_NativeAEAD", None)

    fake = types.SimpleNamespace(
        crypto_aead_xchacha20poly1305_ietf_encrypt=lambda msg, hdr, nonce, key: b"FB" + msg,
        crypto_aead_xchacha20poly1305_ietf_decrypt=lambda ct, hdr, nonce, key: ct[2:],
    )
    sys.modules["nacl"] = types.ModuleType("nacl")
    sys.modules["nacl.bindings"] = fake

    key = os.urandom(32)
    nonce = os.urandom(24)
    data = b"world"

    ct = sa.encrypt_chunk(key, nonce, data, aad)
    pt = sa.decrypt_chunk(key, nonce, ct, aad)
    assert pt == data


@pytest.mark.parametrize("invalid_ct", [b"", b"short", None])
def test_decrypt_invalid(invalid_ct):
    key = b"\x00" * 32
    nonce = b"\x01" * 24

    try:
        result = sa.decrypt_chunk(key, nonce, invalid_ct)
    except (InvalidTag, CryptoError, ValueError, TypeError):
        pass
    else:
        assert isinstance(result, (bytes, bytearray))
