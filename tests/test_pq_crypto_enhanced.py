# tests/test_pq_crypto_enhanced.py

from zilant_prime_core.utils.pq_crypto import OpaqueClient


def test_opaque_client_register_and_login_prints(capsys):
    client = OpaqueClient("https://example.com")
    client.register("user1")
    out = capsys.readouterr().out.strip()
    assert out == "Registering user1 at https://example.com"

    client.login("user2")
    out = capsys.readouterr().out.strip()
    assert out == "Logging in user2 at https://example.com"
