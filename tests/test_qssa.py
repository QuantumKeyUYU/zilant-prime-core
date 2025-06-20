# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

from zilant_prime_core.utils.qssa import QSSA


def test_qssa_unique_addresses():
    q = QSSA()
    pub1, _ = q.generate_address()
    pub2, _ = q.generate_address()
    assert pub1 != pub2
