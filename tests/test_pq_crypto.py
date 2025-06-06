import pytest

from zilant_prime_core.utils import pq_crypto
from zilant_prime_core.utils.pq_crypto import Dilithium2Signature, Kyber768KEM, derive_key_pq


@pytest.mark.skipif(pq_crypto.kyber768 is None, reason="pqclean.kyber768 not installed")
def test_kyber768_generate_and_encapsulate():
    kem = Kyber768KEM()
    pk, sk = kem.generate_keypair()
    ct, ss1 = kem.encapsulate(pk)
    ss2 = kem.decapsulate(sk, ct)
    assert ss1 == ss2
    key = derive_key_pq(ss1)
    assert isinstance(key, bytes) and len(key) == 32


def test_kyber768_missing_dependency(monkeypatch):
    monkeypatch.setattr(pq_crypto, "kyber768", None)
    with pytest.raises(RuntimeError):
        _ = Kyber768KEM()


@pytest.mark.skipif(pq_crypto.dilithium2 is None, reason="pqclean.dilithium2 not installed")
def test_dilithium2_sign_and_verify():
    sigscheme = Dilithium2Signature()
    pk, sk = sigscheme.generate_keypair()
    msg = b"test message"
    sig = sigscheme.sign(sk, msg)
    assert sigscheme.verify(pk, msg, sig) is True
    assert sigscheme.verify(pk, msg + b"x", sig) is False


def test_derive_key_pq_type_error():
    with pytest.raises(TypeError):
        derive_key_pq("bad")  # type: ignore


def test_derive_key_pq_basic():
    key = derive_key_pq(b"secret")
    assert isinstance(key, bytes)
    assert len(key) == 32
