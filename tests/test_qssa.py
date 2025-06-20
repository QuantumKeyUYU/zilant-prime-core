# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

from zilant_prime_core.utils.qssa import QSSA


def test_qssa_shared_secret():
    a = QSSA()
    b = QSSA()
    pub_a, _ = a.generate_keypair()
    pub_b, _ = b.generate_keypair()
    shared1 = a.derive_shared_address(pub_b)
    shared2 = b.derive_shared_address(pub_a)
    assert shared1 == shared2
