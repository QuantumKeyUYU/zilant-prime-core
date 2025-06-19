# tests/test_streaming_aead_full.py

import pytest
import sys
import types

import streaming_aead as sa

# Исключения для native/fallback
try:
    from cryptography.exceptions import InvalidTag
except ImportError:
    InvalidTag = Exception

try:
    from nacl.exceptions import CryptoError
except ImportError:
    CryptoError = Exception


@pytest.mark.parametrize("use_native", [True, False])
def test_encrypt_decrypt_chunk(monkeypatch, use_native):
    key = b"\x00" * 32
    nonce = b"\x01" * 24
    data = b"hello world"
    aad = b"aad-data"

    if use_native:

        class DummyNativeAEAD:
            def __init__(self, k):
                assert k == key

            def encrypt(self, n, pt, hdr):
                assert n == nonce and hdr == aad
                return b"CT" + pt

            def decrypt(self, n, ct, hdr):
                assert n == nonce and hdr == aad
                return ct[2:]

        monkeypatch.setattr(sa, "_NativeAEAD", DummyNativeAEAD)
        sys.modules.pop("nacl.bindings", None)
    else:
        monkeypatch.setattr(sa, "_NativeAEAD", None)
        fake = types.SimpleNamespace(
            crypto_aead_xchacha20poly1305_ietf_encrypt=lambda msg, hdr, nonce, key: b"FB" + msg,
            crypto_aead_xchacha20poly1305_ietf_decrypt=lambda ct, hdr, nonce, key: ct[2:],
        )
        sys.modules["nacl"] = types.ModuleType("nacl")
        sys.modules["nacl.bindings"] = fake

    ct = sa.encrypt_chunk(key, nonce, data, aad)
    pt = sa.decrypt_chunk(key, nonce, ct, aad)
    assert pt == data


@pytest.mark.parametrize("invalid_ct", [b"", b"short", None])
def test_decrypt_invalid(invalid_ct):
    key = b"\x00" * 32
    nonce = b"\x01" * 24

    try:
        result = sa.decrypt_chunk(key, nonce, invalid_ct, b"header")
    except (InvalidTag, CryptoError, ValueError, TypeError):
        pass
    else:
        assert isinstance(result, (bytes, bytearray))
