# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

from zilant_prime_core.utils.qvpn import QVPN


def test_qvpn_toggle():
    q = QVPN()
    assert q.is_enabled() is False
    q.enable()
    assert q.is_enabled() is True
    q.disable()
    assert q.is_enabled() is False
