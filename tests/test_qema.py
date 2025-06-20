# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

from zilant_prime_core.utils.qema import QEMA


def test_qema_anonymize():
    q = QEMA()
    data = {"msg": "hi", "timestamp": "now", "author": "me"}
    anon = q.anonymize(data)
    assert "timestamp" not in anon and "author" not in anon
    assert anon["msg"] == "hi"
