# tests/test_pq_sign_additional.py

import pytest
from types import SimpleNamespace

import zilant_prime_core.utils.pq_sign as pq_sign_module
from zilant_prime_core.utils.pq_sign import PQSign


def test_keygen_sign_verify_fallback(tmp_path):
    # Форсим fallback-ветку Ed25519
    monkey = pytest.MonkeyPatch()
    monkey.setattr(pq_sign_module, "_HAS_OQS", False, raising=False)

    try:
        signer = PQSign()
        sk = tmp_path / "sk.bin"
        pk = tmp_path / "pk.bin"

        signer.keygen(sk, pk)
        assert sk.exists() and pk.exists()

        msg = b"fallback message"
        sig = signer.sign(msg, sk)
        assert isinstance(sig, (bytes, bytearray))
        assert signer.verify(msg, sig, pk)

        bad = b"\x00" * len(sig)
        assert not signer.verify(msg, bad, pk)

        wrong = tmp_path / "nope.bin"
        wrong.write_bytes(pk.read_bytes()[::-1])
        assert not signer.verify(msg, sig, wrong)

    finally:
        monkey.undo()


class FakeOqsSig:
    def __init__(self, alg):
        self.alg = alg
        self._pk = b"FAKEPK"
        self._sk = b"FAKESK"

    def generate_keypair(self):
        return (self._pk, self._sk)

    def sign(self, message, sk_bytes):
        assert sk_bytes == self._sk
        return b"SIG:" + message

    def verify(self, message, signature, pk_bytes):
        return signature == b"SIG:" + message and pk_bytes == self._pk


def test_keygen_sign_verify_oqs(tmp_path):
    # Форсим ветку OQS и подсовываем FakeOqsSig
    monkey = pytest.MonkeyPatch()
    fake_oqs = SimpleNamespace(Signature=FakeOqsSig)
    monkey.setattr(pq_sign_module, "oqs", fake_oqs, raising=False)
    monkey.setattr(pq_sign_module, "_HAS_OQS", True, raising=False)

    try:
        signer = PQSign()
        sk = tmp_path / "oqs_sk.bin"
        pk = tmp_path / "oqs_pk.bin"

        signer.keygen(sk, pk)
        assert sk.read_bytes() == b"FAKESK"
        assert pk.read_bytes() == b"FAKEPK"

        msg = b"hello oqs"
        sig = signer.sign(msg, sk)
        assert sig == b"SIG:" + msg
        assert signer.verify(msg, sig, pk)

        bad_pk = tmp_path / "bad_pk.bin"
        bad_pk.write_bytes(b"XXXX")
        assert not signer.verify(msg, sig, bad_pk)

    finally:
        monkey.undo()
