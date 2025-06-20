# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

from __future__ import annotations

import pytest

from zilant_prime_core.utils.qal import QAL


@pytest.mark.parametrize("size", [1, 3, 5])
def test_qal_sign_verify(tmp_path, size: int) -> None:
    group = QAL(size, tmp_path)
    msg = b"quantum"
    sig = group.sign(msg, size - 1)
    pubs = [p.read_bytes() for _, p in group.keys]
    assert group.verify(msg, sig, pubs) is True


def test_qal_foreign_signature(tmp_path) -> None:
    group1 = QAL(3, tmp_path / "a")
    group2 = QAL(3, tmp_path / "b")
    sig = group1.sign(b"hi", 0)
    pubs = [p.read_bytes() for _, p in group2.keys]
    assert group2.verify(b"hi", sig, pubs) is False


def test_qal_verify_fail(tmp_path) -> None:
    group = QAL(2, tmp_path)
    sig = group.sign(b"hello", 0)
    pubs = [p.read_bytes() for _, p in group.keys]
    assert group.verify(b"other", sig, pubs) is False
