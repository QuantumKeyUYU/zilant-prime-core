import pytest

from zilant_prime_core.crypto.signature import (
    generate_keypair,
    sign,
    verify,
    SignatureError,
    SIG_SIZE,
)

def test_verify_invalid_pub_or_sig():
    priv, pub = generate_keypair()
    sig = sign(priv, b"hello")

    # слишком короткий публичный ключ
    assert not verify(b"short", b"msg", sig)
    # слишком короткая/длинная подпись
    assert not verify(pub, b"msg", b"shortsig")
    assert not verify(pub, b"msg", b"\x00" * (SIG_SIZE + 1))
    # корректная длина, но неправильное содержимое
    assert not verify(pub, b"msg", b"\x00" * SIG_SIZE)

def test_verify_invalid_inputs_strict():
    priv, pub = generate_keypair()
    sig = sign(priv, b"hello")
    bad_sig = sig[:-1]

    # при strict=True любые некорректные аргументы должны бросать SignatureError
    with pytest.raises(SignatureError):
        verify(pub, b"hello", bad_sig, strict=True)

    with pytest.raises(SignatureError):
        verify(b"short", b"msg", sig, strict=True)

    with pytest.raises(SignatureError):
        verify(pub, "not-bytes-message", sig, strict=True)

    with pytest.raises(SignatureError):
        verify(pub, b"msg", b"shortsig", strict=True)
