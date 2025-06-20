import pytest

from zilant_prime_core.utils.auth import _HAS_OQS, OpaqueAuth


@pytest.fixture
def tmp_auth(tmp_path):
    return tmp_path / "auth"


@pytest.mark.skipif(not _HAS_OQS, reason="oqs library not installed")
def test_register_and_login(tmp_auth):
    auth = OpaqueAuth()
    auth.register("bob", "secret", tmp_auth)
    assert (tmp_auth / "bob.cred").exists()
    assert auth.login("bob", "secret", tmp_auth)
    assert not auth.login("bob", "wrong", tmp_auth)
