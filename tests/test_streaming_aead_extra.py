# tests/test_streaming_aead_extra.py

import os
import sys
import types

import src.streaming_aead as sa


def test_native_encrypt_decrypt(monkeypatch):
    """
    Пробуем нативную ветку (_NativeAEAD != None) с dummy-классом,
    проверяем, что и encrypt_chunk, и decrypt_chunk используют наш валидатор.
    """

    class DummyAEAD:
        def __init__(self, key):
            # проверим, что ключ передаётся в конструктор
            assert key == TEST_KEY

        def encrypt(self, nonce, plaintext, aad):
            # проверяем корректность аргументов
            assert nonce == TEST_NONCE
            assert plaintext == TEST_DATA
            assert aad == TEST_AAD or aad == b""
            return b"E|" + plaintext

        def decrypt(self, nonce, ciphertext, aad):
            # тот же набор проверок
            assert nonce == TEST_NONCE
            assert ciphertext.startswith(b"E|")
            assert aad == TEST_AAD or aad == b""
            # «расшифровываем» обратно
            return ciphertext[len(b"E|") :]

    # Параметры для теста
    TEST_KEY = os.urandom(32)
    TEST_NONCE = os.urandom(24)
    TEST_DATA = b"hello-native"
    TEST_AAD = b"hdr"

    # Внедряем DummyAEAD вместо реального
    monkeypatch.setattr(sa, "_NativeAEAD", DummyAEAD)

    # encrypt_chunk
    ct = sa.encrypt_chunk(TEST_KEY, TEST_NONCE, TEST_DATA, TEST_AAD)
    assert ct == b"E|" + TEST_DATA

    # decrypt_chunk
    pt = sa.decrypt_chunk(TEST_KEY, TEST_NONCE, ct, TEST_AAD)
    assert pt == TEST_DATA


def test_fallback_encrypt_decrypt(monkeypatch):
    """
    Пробуем fallback-ветку (_NativeAEAD is None) с подмешанным nacl.bindings.
    """
    # Форсим отсутствие нативного бэкенда
    monkeypatch.setattr(sa, "_NativeAEAD", None, raising=False)

    # Подменяем модуль nacl.bindings
    fake = types.SimpleNamespace(
        crypto_aead_xchacha20poly1305_ietf_encrypt=lambda msg, aad, nonce, key: b"F|" + msg,
        crypto_aead_xchacha20poly1305_ietf_decrypt=lambda ct, aad, nonce, key: ct[len(b"F|") :],
    )
    sys.modules["nacl"] = types.ModuleType("nacl")
    sys.modules["nacl.bindings"] = fake

    TEST_KEY = os.urandom(32)
    TEST_NONCE = os.urandom(24)
    TEST_DATA = b"fallback-data"

    # encrypt (aad=None → header=b"")
    ct = sa.encrypt_chunk(TEST_KEY, TEST_NONCE, TEST_DATA, None)
    assert ct == b"F|" + TEST_DATA

    # decrypt (aad omitted → header=b"")
    pt = sa.decrypt_chunk(TEST_KEY, TEST_NONCE, ct, None)
    assert pt == TEST_DATA
