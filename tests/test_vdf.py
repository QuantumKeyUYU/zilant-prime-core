# tests/test_vdf.py

import pytest
import time
import hashlib
import sys
import builtins  # For debug_print fallback

# Function to ensure printing works during tests if default print doesn't
def debug_print(*args, **kwargs):
    """A simple print function that might work better in test environments."""
    builtins.print("DEBUG:", *args, **kwargs)

from zilant_prime_core.vdf.vdf import (
    generate_posw_sha256,
    verify_posw_sha256,
    VDFVerificationError,
)

# Basic test for correctness
def test_posw_correctness():
    seed = b"test_seed"
    steps = 100
    proof = generate_posw_sha256(seed, steps)
    assert isinstance(proof, bytes)
    assert len(proof) == hashlib.sha256().digest_size  # SHA256 hash size

    is_valid = verify_posw_sha256(seed, proof, steps)
    assert is_valid is True

    # Tamper with the proof
    tampered_proof = bytearray(proof)
    tampered_proof[0] ^= 0xFF  # Flip a bit
    is_valid_tampered = verify_posw_sha256(seed, bytes(tampered_proof), steps)
    assert is_valid_tampered is False

    # Verify with wrong steps
    is_valid_wrong_steps = verify_posw_sha256(seed, proof, steps + 1)
    assert is_valid_wrong_steps is False

    # Verify with wrong seed
    is_valid_wrong_seed = verify_posw_sha256(b"wrong_seed", proof, steps)
    assert is_valid_wrong_seed is False

# Test edge cases for correctness
def test_posw_correctness_edge_cases():
    seed = b"edge_case_seed"
    steps = 1  # Minimum steps

    proof = generate_posw_sha256(seed, steps)
    assert isinstance(proof, bytes)
    assert len(proof) == hashlib.sha256().digest_size

    is_valid = verify_posw_sha256(seed, proof, steps)
    assert is_valid is True

    # Tamper with proof (steps=1)
    tampered_proof = bytearray(proof)
    tampered_proof[0] ^= 0xFF
    is_valid_tampered = verify_posw_sha256(seed, bytes(tampered_proof), steps)
    assert is_valid_tampered is False

# Test for expected errors
def test_posw_invalid_input():
    with pytest.raises(ValueError, match="Steps must be a positive integer."):
        generate_posw_sha256(b"seed", 0)
    with pytest.raises(ValueError, match="Steps must be a positive integer."):
        verify_posw_sha256(b"seed", hashlib.sha256().digest(), 0)

    with pytest.raises(ValueError, match="Seed must be bytes."):
        generate_posw_sha256("seed_string", 100)  # type: ignore
    with pytest.raises(ValueError, match="Seed must be bytes."):
        verify_posw_sha256("seed_string", hashlib.sha256().digest(), 100)  # type: ignore

    # Verify with incorrect proof length
    assert verify_posw_sha256(b"seed", b"short_proof", 100) is False
    assert verify_posw_sha256(
        b"seed", b"a" * (hashlib.sha256().digest_size + 1), 100
    ) is False

# Test VDF verification error type (if updated to raise exception)
def test_posw_verification_error():
    seed = b"test_seed"
    steps = 100
    proof = generate_posw_sha256(seed, steps)

    # Tamper with the proof to cause a verification failure
    tampered_proof = bytearray(proof)
    tampered_proof[0] ^= 0xFF

    # Should return False, or raise VDFVerificationError if implemented that way
    result = verify_posw_sha256(seed, bytes(tampered_proof), steps)
    assert result is False

# Performance test for VDF (PoSW) — skip on Windows due to timing variability
@pytest.mark.skipif(sys.platform.startswith("win"), reason="Skip flaky performance test on Windows")
def test_posw_performance():
    seed = b"performance_seed"
    steps = 100000  # Adjust for your hardware if needed

    start_time = time.perf_counter()
    proof = generate_posw_sha256(seed, steps)
    gen_time = time.perf_counter() - start_time
    print(f"\nPoSW generation time for {steps} steps: {gen_time:.4f} seconds")

    start_time = time.perf_counter()
    is_valid = verify_posw_sha256(seed, proof, steps)
    verify_time = time.perf_counter() - start_time
    print(f"PoSW verification time for {steps} steps: {verify_time:.4f} seconds")

    assert is_valid is True
    # Allow 40% tolerance
    assert abs(gen_time - verify_time) / gen_time < 0.4
