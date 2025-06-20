# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

from zilant_prime_core.utils.zkqp import ZKQP


def test_zkqp_prove_verify(tmp_path):
    z = ZKQP(tmp_path)
    data = b"secret"
    commit, proof = z.prove(data)
    assert z.verify(data, commit, proof) is True


def test_zkqp_verify_fail(tmp_path):
    z = ZKQP(tmp_path)
    data = b"secret"
    commit, proof = z.prove(data)
    assert z.verify(b"other", commit, proof) is False
