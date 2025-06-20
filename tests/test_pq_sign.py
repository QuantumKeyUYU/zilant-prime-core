# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

import json
import os
import shutil
import tempfile
import pytest
from pathlib import Path
from zilant_prime_core.utils.pq_sign import PQSign


@pytest.fixture
def temp_keys_dir(tmp_path):
    d = tmp_path / "keys"
    d.mkdir()
    yield d
    # cleanup not needed for tmp_path


def test_keygen_creates_files(temp_keys_dir):
    priv = temp_keys_dir / "pq_priv.key"
    pub = temp_keys_dir / "pq_pub.key"
    signer = PQSign()
    signer.keygen(priv, pub)
    assert priv.exists() and priv.stat().st_size > 0
    assert pub.exists() and pub.stat().st_size > 0


def test_sign_and_verify_success(temp_keys_dir):
    priv = temp_keys_dir / "pq_priv.key"
    pub = temp_keys_dir / "pq_pub.key"
    signer = PQSign()
    signer.keygen(priv, pub)

    data = b"hello world"
    sig = signer.sign(data, priv)
    assert isinstance(sig, (bytes, bytearray))
    ok = signer.verify(data, sig, pub)
    assert ok is True


def test_verify_fails_on_corruption(temp_keys_dir):
    priv = temp_keys_dir / "pq_priv.key"
    pub = temp_keys_dir / "pq_pub.key"
    signer = PQSign()
    signer.keygen(priv, pub)

    data = b"foo"
    sig = signer.sign(data, priv)
    # подпись испорчена
    bad = sig[:-1] + bytes([sig[-1] ^ 0xFF])
    ok = signer.verify(data, bad, pub)
    assert ok is False
