# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

import base64
import json

import pytest

from zilant_prime_core.counter import DistributedCounter, SecurityError


def test_increment_persist_and_reload(tmp_path):
    path = tmp_path / "c.bin"
    ctr1 = DistributedCounter(path, b"k" * 32)
    assert ctr1.increment() == 1
    assert ctr1.increment() == 2

    ctr2 = DistributedCounter(path, b"k" * 32)
    assert ctr2.verify_and_load() == 2
    assert ctr2.increment() == 3
    assert ctr2.verify_and_load() == 3


def test_hmac_tamper_detection(tmp_path):
    path = tmp_path / "c.bin"
    ctr = DistributedCounter(path, b"z" * 32)
    ctr.increment()
    plain = json.loads(ctr._decrypt(path.read_bytes()).decode())
    plain["hmac"] = base64.b64encode(b"bad" * 10 + b"xx").decode()
    path.write_bytes(ctr._encrypt(json.dumps(plain).encode()))
    with pytest.raises(SecurityError):
        ctr.verify_and_load()
