# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

from zilant_prime_core.utils.quantum_ra import QuantumRA


def test_quantum_ra(tmp_path):
    ra = QuantumRA(tmp_path)
    info = b"device"
    sig = ra.attest(info)
    assert ra.verify(info, sig) is True
    assert ra.verify(b"other", sig) is False
