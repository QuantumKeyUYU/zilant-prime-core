# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

# tests/test_vdf.py

import builtins
import hashlib
import sys
import time

import pytest

from zilant_prime_core.vdf.vdf import generate_posw_sha256, verify_posw_sha256


def debug_print(*args, **kwargs):
    builtins.print("DEBUG:", *args, **kwargs)


def test_posw_correctness():
    seed = b"test_seed"
    steps = 100
    proof = generate_posw_sha256(seed, steps)
    assert isinstance(proof, bytes)
    assert len(proof) == hashlib.sha256().digest_size

    assert verify_posw_sha256(seed, proof, steps) is True

    # Tamper proof
    bad = bytearray(proof)
    bad[0] ^= 0xFF
    assert verify_posw_sha256(seed, bytes(bad), steps) is False

    # Wrong steps or seed
    assert verify_posw_sha256(seed, proof, steps + 1) is False
    assert verify_posw_sha256(b"wrong", proof, steps) is False


def test_posw_correctness_edge_cases():
    seed = b"edge"
    steps = 1
    proof = generate_posw_sha256(seed, steps)
    assert verify_posw_sha256(seed, proof, steps) is True
    bad = bytearray(proof)
    bad[0] ^= 0xFF
    assert verify_posw_sha256(seed, bytes(bad), steps) is False


def test_posw_invalid_input():
    with pytest.raises(ValueError, match="Steps must be a positive integer."):
        generate_posw_sha256(b"seed", 0)
    with pytest.raises(ValueError, match="Steps must be a positive integer."):
        verify_posw_sha256(b"seed", hashlib.sha256().digest(), 0)

    with pytest.raises(ValueError, match="Seed must be bytes."):
        generate_posw_sha256("seed", 1)  # type: ignore
    with pytest.raises(ValueError, match="Seed must be bytes."):
        verify_posw_sha256("seed", hashlib.sha256().digest(), 1)  # type: ignore

    # Incorrect proof length → just False
    assert verify_posw_sha256(b"seed", b"short", 10) is False
    assert verify_posw_sha256(b"seed", b"x" * (hashlib.sha256().digest_size + 1), 10) is False


def test_posw_verification_error():
    seed = b"test"
    steps = 10
    proof = generate_posw_sha256(seed, steps)
    bad = bytearray(proof)
    bad[0] ^= 0xFF

    # Should simply return False (no exception)
    assert verify_posw_sha256(seed, bytes(bad), steps) is False


@pytest.mark.skipif(sys.platform.startswith("win"), reason="Skip flaky performance test on Windows")
def test_posw_performance():
    seed = b"perf"
    steps = 100_000

    start = time.perf_counter()
    proof = generate_posw_sha256(seed, steps)
    dt1 = time.perf_counter() - start

    start = time.perf_counter()
    ok = verify_posw_sha256(seed, proof, steps)
    dt2 = time.perf_counter() - start

    assert ok is True
    # timings within 60% to avoid flakiness on slow environments
    assert abs(dt1 - dt2) / dt1 < 0.6
