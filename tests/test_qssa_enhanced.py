# tests/test_qssa_enhanced.py

import pytest
from cryptography.hazmat.primitives.asymmetric import x25519

from zilant_prime_core.utils.qssa import QSSA


def test_generate_keypair_outputs_32_bytes_and_sets_private(tmp_path):
    q = QSSA()
    pub, priv = q.generate_keypair()
    # оба ключа сырые по 32 байта
    assert isinstance(pub, bytes) and len(pub) == 32
    assert isinstance(priv, bytes) and len(priv) == 32
    # приватный объект внутри класса установлен
    assert q._private is not None and isinstance(q._private, x25519.X25519PrivateKey)


def test_derive_shared_address_consistency_and_length():
    alice = QSSA()
    bob = QSSA()
    pub_a, _ = alice.generate_keypair()
    pub_b, _ = bob.generate_keypair()
    shared1 = alice.derive_shared_address(pub_b)
    shared2 = bob.derive_shared_address(pub_a)
    # общий секрет совпадает и всегда 32 байта (HKDF-SHA256)
    assert shared1 == shared2 and len(shared1) == 32


def test_derive_shared_address_raises_if_no_generate():
    q = QSSA()
    with pytest.raises(ValueError) as exc:
        q.derive_shared_address(b"\x00" * 32)
    assert "must be called first" in str(exc.value)
