# tests/test_vdf_property.py

from hypothesis import given, strategies as st
import pytest

from zilant_prime_core.vdf.vdf import generate_posw_sha256, verify_posw_sha256


@given(
    seed=st.binary(min_size=1, max_size=64),
    steps=st.integers(min_value=1, max_value=100),
)
def test_posw_roundtrip(seed, steps):
    proof = generate_posw_sha256(seed, steps)
    # всегда корректно верифицируется
    assert verify_posw_sha256(seed, proof, steps)


@given(seed=st.binary(), steps=st.integers(max_value=0))
def test_posw_invalid_steps(seed, steps):
    with pytest.raises(ValueError):
        generate_posw_sha256(seed, steps)
    with pytest.raises(ValueError):
        verify_posw_sha256(seed, b"", steps)


@given(
    seed=st.binary(min_size=1), steps=st.integers(min_value=1), bad_proof=st.binary()
)
def test_posw_bad_proof_returns_false(seed, steps, bad_proof):
    # неверная длина или содержимое → False
    if len(bad_proof) != __import__("hashlib").sha256().digest_size:
        assert verify_posw_sha256(seed, bad_proof, steps) is False
    else:
        # если по длине норм, но данные искаженны
        assert verify_posw_sha256(seed, bad_proof, steps) is False
