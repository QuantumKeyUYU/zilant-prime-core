# tests/test_auth_enhanced.py

import pytest
from types import SimpleNamespace

import zilant_prime_core.utils.auth as auth_module
from zilant_prime_core.utils.auth import OpaqueAuth


def test_init_requires_oqs(monkeypatch):
    # <--- lines 16–18 in __init__
    monkeypatch.setattr(auth_module, "_HAS_OQS", False, raising=False)
    with pytest.raises(RuntimeError, match="OPAQUE support requires oqs library"):
        OpaqueAuth()


def test_register_and_login_happy(monkeypatch, tmp_path):
    # включаем искусственный oqs и KeyEncapsulation
    fake_oqs = SimpleNamespace(KeyEncapsulation=lambda alg: None)
    monkeypatch.setattr(auth_module, "_HAS_OQS", True, raising=False)
    monkeypatch.setattr(auth_module, "oqs", fake_oqs, raising=False)

    auth = OpaqueAuth()
    # register → файл создаётся
    auth.register("alice", "pwd123", tmp_path)
    cred = tmp_path / "alice.cred"
    assert cred.exists() and cred.read_text().startswith("$argon2")

    # успешный логин
    assert auth.login("alice", "pwd123", tmp_path) is True
    # неуспешный логин (неверный пароль)
    assert auth.login("alice", "wrong", tmp_path) is False
    # несуществующий юзер → FileNotFoundError
    with pytest.raises(FileNotFoundError):
        auth.login("bob", "x", tmp_path)
