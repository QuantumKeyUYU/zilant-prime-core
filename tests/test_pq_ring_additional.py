# tests/test_pq_ring_additional.py

import json
import pytest

import zilant_prime_core.utils.pq_ring as pq_ring_module
from zilant_prime_core.utils.pq_ring import PQRing


def test_ring_fallback_sign_verify_and_save(tmp_path):
    # Форсим fallback-ветку Ed25519
    monkey = pytest.MonkeyPatch()
    monkey.setattr(pq_ring_module, "_HAS_OQS", False, raising=False)

    try:
        ring = PQRing(alg="Ed25519", group_size=3, work_dir=tmp_path)
        assert len(ring.keys) == 3

        msg = b"ring fallback"
        sig = ring.sign(msg, signer_index=1)
        assert isinstance(sig, (bytes, bytearray))
        assert ring.verify(msg, sig)

        # неверная подпись → False
        assert not ring.verify(msg, b"\x00" * len(sig))

        # несуществующий индекс → IndexError
        with pytest.raises(IndexError):
            ring.sign(msg, signer_index=5)

        # сохраняем JSON и сверяем
        ring._save_keys()
        f = tmp_path / "ring_keys.json"
        data = json.loads(f.read_text())
        assert isinstance(data, list) and len(data) == 3
        for idx, rec in enumerate(data):
            assert bytes.fromhex(rec["pub"]) == ring.keys[idx][0]
            assert bytes.fromhex(rec["priv"]) == ring.keys[idx][1]

    finally:
        monkey.undo()


class FakeOqsRing:
    def __init__(self, alg):
        self.alg = alg
        self._pub = b"PQRINGPUB"
        self._priv = b"PQRINGSK"

    def generate_keypair(self):
        return (self._pub, self._priv)

    def sign(self, message, priv_bytes):
        assert priv_bytes == self._priv
        return b"RINGSIG:" + message

    def verify(self, message, signature, pub_bytes):
        return signature == b"RINGSIG:" + message and pub_bytes == self._pub


def test_ring_oqs_sign_verify_and_save(tmp_path):
    # Форсим ветку OQS и подсовываем FakeOqsRing
    monkey = pytest.MonkeyPatch()
    monkey.setattr(pq_ring_module, "_HAS_OQS", True, raising=False)
    monkey.setattr(pq_ring_module, "Signature", FakeOqsRing, raising=False)

    try:
        ring = PQRing(alg="FakeAlg", group_size=2, work_dir=tmp_path)
        assert len(ring.keys) == 2

        msg = b"oqs ring"
        for i in range(2):
            sig = ring.sign(msg, signer_index=i)
            assert sig == b"RINGSIG:" + msg
            assert ring.verify(msg, sig)

        # неверный индекс
        with pytest.raises(IndexError):
            ring.sign(msg, signer_index=2)

        # сохраняем JSON и сверяем
        ring._save_keys()
        f = tmp_path / "ring_keys.json"
        j = json.loads(f.read_text())
        assert isinstance(j, list) and len(j) == 2
        for rec in j:
            assert "pub" in rec and "priv" in rec
            # корректный hex
            assert bytes.fromhex(rec["pub"])
            assert bytes.fromhex(rec["priv"])
    finally:
        monkey.undo()
