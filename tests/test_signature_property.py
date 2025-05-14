# tests/test_signature_property.py

from hypothesis import given, strategies as st
import pytest

from zilant_prime_core.crypto.signature import generate_keypair, sign, verify, SignatureError

@given(msg=st.binary(min_size=0, max_size=1024))
def test_sign_verify_consistency(msg):
    pub, priv = generate_keypair()
    sig = sign(priv, msg)
    assert isinstance(sig, (bytes, bytearray))
    # Корректная верификация
    assert verify(pub, msg, sig)

def test_sign_invalid_key():
    # слишком короткий приватный ключ
    with pytest.raises(SignatureError):
        sign(b"short", b"msg")

@given(bad_pub=st.binary(min_size=0, max_size=31), msg=st.binary(), sig=st.binary(min_size=1, max_size=64))
def test_verify_invalid_inputs(bad_pub, msg, sig):
    # неверные публичный ключ, сообщение или сигнатура — всегда False
    assert verify(bad_pub, msg, sig) is False
