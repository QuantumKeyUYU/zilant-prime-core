from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

import pqcrypto


def test_hybrid_encrypt_decrypt(monkeypatch):
    class DummyHybrid:
        def encapsulate(self, pub):
            return (b"CT", b"SS", b"X" * 32, b"SX", b"KEY")

        def decapsulate(self, priv, ct):
            ct_pq, epk, _ = ct
            assert ct_pq == b"CT" and epk == b"X" * 32
            return b"KEY"

    class DummyAEAD:
        def __init__(self, key):
            self.key = key

        def encrypt(self, nonce, plaintext, aad):
            return plaintext[::-1]

        def decrypt(self, nonce, ciphertext, aad):
            return ciphertext[::-1]

    monkeypatch.setattr(pqcrypto, "HybridKEM", lambda: DummyHybrid())
    monkeypatch.setattr(pqcrypto, "ChaCha20Poly1305", DummyAEAD)
    monkeypatch.setattr(pqcrypto.os, "urandom", lambda n: b"N" * n)

    enc, ct = pqcrypto.hybrid_encrypt((b"pkpq", b"pkx"), b"data", b"aad")
    assert enc.startswith(b"CT" + b"X" * 32 + b"N" * 12)
    plain = pqcrypto.hybrid_decrypt((b"skpq", b"skx"), enc, ct, b"aad")
    assert plain == b"data"


def test_dual_sign_verify(monkeypatch):
    class DummyDilithium:
        @staticmethod
        def sign(msg, sk):
            return b"PQ" + msg

        @staticmethod
        def verify(msg, sig, pk):
            return sig == b"PQ" + msg

    monkeypatch.setattr(pqcrypto, "dilithium3", DummyDilithium)
    sk = b"\x11" * 32
    pk = (
        ed25519.Ed25519PrivateKey.from_private_bytes(sk)
        .public_key()
        .public_bytes(encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)
    )
    sig = pqcrypto.dual_sign(b"msg", sk, b"pqsk")
    assert pqcrypto.dual_verify(b"msg", sig, pk, b"pqpk")
    assert not pqcrypto.dual_verify(b"bad", sig, pk, b"pqpk")
