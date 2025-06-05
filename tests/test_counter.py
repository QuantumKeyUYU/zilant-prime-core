# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

from zilant_prime_core.utils.counter import Counter


def test_counter_increment():
    c = Counter()
    assert c.increment() == 1
    assert c.increment() == 2
