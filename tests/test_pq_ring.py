# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

import pytest
from pathlib import Path

from zilant_prime_core.utils.pq_ring import PQRing


@pytest.mark.parametrize("group_size", [2, 5])
def test_ring_signature_valid(tmp_path: Path, group_size: int) -> None:
    ring = PQRing("Dilithium2", group_size, tmp_path)
    msg = b"Quantum message"
    signature = ring.sign(msg, signer_index=0)
    assert ring.verify(msg, signature) is True


def test_ring_signature_invalid_message(tmp_path: Path) -> None:
    ring = PQRing("Dilithium2", 3, tmp_path)
    signature = ring.sign(b"valid", signer_index=1)
    assert ring.verify(b"invalid", signature) is False


def test_ring_signature_invalid_signature(tmp_path: Path) -> None:
    ring1 = PQRing("Dilithium2", 3, tmp_path / "ring1")
    ring2 = PQRing("Dilithium2", 3, tmp_path / "ring2")
    signature = ring1.sign(b"message", signer_index=1)
    assert ring2.verify(b"message", signature) is False
