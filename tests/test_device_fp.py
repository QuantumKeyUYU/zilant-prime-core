# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

from zilant_prime_core.utils.device_fp import get_device_fingerprint


def test_device_fp_returns_string():
    assert isinstance(get_device_fingerprint(), str)
