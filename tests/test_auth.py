import pytest

from zilant_prime_core.utils.auth import OpaqueAuth


@pytest.fixture
def tmp_auth(tmp_path):
    return tmp_path / "auth"


def test_register_and_login(tmp_auth):
    auth = OpaqueAuth()
    auth.register("bob", "secret", tmp_auth)
    assert (tmp_auth / "bob.cred").exists()
    assert auth.login("bob", "secret", tmp_auth)
    assert not auth.login("bob", "wrong", tmp_auth)
