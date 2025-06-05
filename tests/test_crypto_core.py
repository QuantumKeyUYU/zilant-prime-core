from zilant_prime_core.utils.crypto_wrapper import (
    derive_sk0_from_fp,
    derive_sk1,
    get_sk_bytes,
    release_sk,
)
from zilant_prime_core.utils.device_fp import get_device_fp


def test_crypto_core_roundtrip():
    fp = get_device_fp()
    h0 = derive_sk0_from_fp(fp)
    h1 = derive_sk1(h0, b"password")
    key = get_sk_bytes(h1)
    assert len(key) == 32
    release_sk(h0)
    release_sk(h1)
