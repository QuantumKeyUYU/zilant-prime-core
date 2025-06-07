# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core Contributors
import secrets

from zilant_prime_core import uniform_container as container


def test_uniform_pack_unpack():
    meta = {"foo": "bar"}
    payload = secrets.token_bytes(100)
    key = secrets.token_bytes(32)
    blob = container.pack(meta, payload, key)
    assert (len(blob) - 12 - 16) % 4096 == 0
    m2, p2 = container.unpack(blob, key)
    assert m2 == meta
    assert p2 == payload
