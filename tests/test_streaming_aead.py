import builtins
import importlib

import streaming_aead


def test_roundtrip():
    key = b"k" * 32
    nonce = b"n" * 24
    msg = b"hello"
    aad = b"aad"
    ct = streaming_aead.encrypt_chunk(key, nonce, msg, aad)
    assert streaming_aead.decrypt_chunk(key, nonce, ct, aad) == msg


def test_fallback(monkeypatch):
    key = b"k" * 32
    nonce = b"n" * 24
    msg = b"hi"
    aad = b""
    orig_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "cryptography.hazmat.primitives.ciphers.aead":
            raise ImportError()
        return orig_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    mod = importlib.reload(streaming_aead)
    ct = mod.encrypt_chunk(key, nonce, msg, aad)
    assert mod.decrypt_chunk(key, nonce, ct, aad) == msg
    monkeypatch.setattr(builtins, "__import__", orig_import)
    importlib.reload(streaming_aead)
