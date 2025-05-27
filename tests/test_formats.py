# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

import pytest

from zilant_prime_core.utils.formats import from_b64, from_hex, to_b64, to_hex


def test_hex_roundtrip():
    data = b"\x00\xff\x10"
    s = to_hex(data)
    assert s == "00ff10"
    assert from_hex(s) == data


def test_hex_invalid():
    with pytest.raises(ValueError):
        from_hex("gg")


def test_b64_roundtrip():
    data = b"foobar"
    s = to_b64(data)
    assert from_b64(s) == data


def test_b64_invalid():
    with pytest.raises(ValueError):
        from_b64("!!! not base64 !!!")
