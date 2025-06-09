# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

from types import SimpleNamespace

import pytest

import zilant_prime_core.utils.pq_crypto as pq
from zilant_prime_core.utils.pq_crypto import (
    KEM,
    Dilithium2Signature,
    Kyber768KEM,
    OQSKyberKEM,
    SignatureScheme,
    derive_key_pq,
)


@pytest.mark.skipif(pq.kyber768 is None, reason="pqclean.kyber768 not installed")
def test_kyber768_generate_and_encapsulate_real():
    kem = Kyber768KEM()
    pk, sk = kem.generate_keypair()
    ct, ss1 = kem.encapsulate(pk)
    ss2 = kem.decapsulate(sk, ct)
    assert ss1 == ss2
    key = derive_key_pq(ss1)
    assert isinstance(key, bytes) and len(key) == 32


@pytest.mark.skipif(pq.dilithium2 is None, reason="pqclean.dilithium2 not installed")
def test_dilithium2_sign_and_verify_real():
    sigscheme = Dilithium2Signature()
    pk, sk = sigscheme.generate_keypair()
    msg = b"hello"
    sig = sigscheme.sign(sk, msg)
    assert sigscheme.verify(pk, msg, sig) is True
    assert sigscheme.verify(pk, msg + b"x", sig) is False


def test_kyber768_missing_dependency(monkeypatch):
    monkeypatch.setattr(pq, "kyber768", None)
    with pytest.raises(RuntimeError):
        Kyber768KEM()


def test_dilithium2_missing_dependency(monkeypatch):
    monkeypatch.setattr(pq, "dilithium2", None)
    with pytest.raises(RuntimeError):
        Dilithium2Signature()


def test_oqs_missing_dependency(monkeypatch):
    monkeypatch.setattr(pq, "oqs", None)
    with pytest.raises(RuntimeError):
        OQSKyberKEM()


def test_signature_scheme_not_instantiable():
    with pytest.raises(TypeError):
        SignatureScheme()


def test_kem_not_instantiable():
    with pytest.raises(TypeError):
        KEM()


def test_derive_key_pq_type_error():
    with pytest.raises(TypeError):
        derive_key_pq("not-bytes")  # type: ignore


def test_derive_key_pq_basic():
    key = derive_key_pq(b"secret", length=16)
    assert isinstance(key, bytes)
    assert len(key) == 16


def test_kyber768_heavy_branches(monkeypatch):
    # Фейковый модуль pqclean.kyber768 с CIPHERTEXT_SIZE
    fake = SimpleNamespace(
        generate_keypair=lambda: (b"PUBL", b"PRIV"),
        encapsulate=lambda pub: (b"CTTT", b"SSSS"),
        decapsulate=lambda ct, sk: b"SSSS",
        CIPHERTEXT_SIZE=123,
    )
    monkeypatch.setattr(pq, "kyber768", fake)

    kem = Kyber768KEM()
    assert kem.generate_keypair() == (b"PUBL", b"PRIV")
    assert kem.encapsulate(b"PUBL") == (b"CTTT", b"SSSS")
    assert kem.decapsulate(b"PRIV", b"CTTT") == b"SSSS"
    assert kem.ciphertext_length() == 123

    # Удаляем CIPHERTEXT_SIZE и проверяем fallback-путь
    del fake.CIPHERTEXT_SIZE
    # staticmethod fallback: вызывает kyber768.generate_keypair/encapsulate
    length = Kyber768KEM.ciphertext_length()
    assert length == len(fake.encapsulate(fake.generate_keypair()[0])[0])


def test_dilithium2_heavy_branches(monkeypatch):
    # Фейковый модуль pqclean.dilithium2 с нормальным verify
    fake = SimpleNamespace(
        generate_keypair=lambda: (b"PK", b"SK"),
        sign=lambda msg, sk: b"SIGG",
        verify=lambda msg, sig, pk: True,
    )
    monkeypatch.setattr(pq, "dilithium2", fake)

    sigscheme = Dilithium2Signature()
    assert sigscheme.generate_keypair() == (b"PK", b"SK")
    assert sigscheme.sign(b"m", b"SK") == b"SIGG"
    assert sigscheme.verify(b"PK", b"m", b"SIGG") is True

    # Имитируем неверную подпись (verify бросает)
    def failing_verify(msg, sig, pk):
        raise Exception("bad sig")

    fake.verify = failing_verify
    sig2 = Dilithium2Signature()
    assert sig2.verify(b"PK", b"m", b"anything") is False


def test_oqskyberkem_heavy(monkeypatch):
    # Фейковый модуль liboqs
    class DummyKEM:
        def __init__(self, alg):
            assert alg == "Kyber768"
            self.details = SimpleNamespace(length_ciphertext=77)

        def generate_keypair(self):
            return (b"OPK", b"OSK")

        def encapsulate(self, pk):
            return (b"OCT", b"OSS")

        def decapsulate(self, ct, sk):
            return b"OSS"

    fake = SimpleNamespace(KeyEncapsulation=lambda alg: DummyKEM(alg))
    monkeypatch.setattr(pq, "oqs", fake)

    kem = OQSKyberKEM()
    assert kem.generate_keypair() == (b"OPK", b"OSK")
    assert kem.encapsulate(b"OPK") == (b"OCT", b"OSS")
    assert kem.decapsulate(b"OSK", b"OCT") == b"OSS"
    assert kem.ciphertext_length() == 77
