# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

from zilant_prime_core.utils.qal import QAL


def test_qal_sign_verify(tmp_path):
    group = QAL(3, tmp_path)
    msg = b"quantum"
    sig = group.sign(msg, 1)
    assert group.verify(msg, sig) is True


def test_qal_verify_fail(tmp_path):
    group = QAL(2, tmp_path)
    msg = b"hello"
    sig = group.sign(msg, 0)
    assert group.verify(b"other", sig) is False
