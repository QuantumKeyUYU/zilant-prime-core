# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

from zilant_prime_core.utils.anti_snapshot import detect_snapshot


def test_detect_snapshot_bool():
    assert detect_snapshot() in (True, False)
