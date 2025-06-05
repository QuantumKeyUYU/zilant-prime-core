from zilant_prime_core.utils.counter import (
    get_monotonic_counter,
    increment_monotonic_counter,
    init_counter_storage,
    set_sk1_handle,
)
from zilant_prime_core.utils.crypto_wrapper import derive_sk0_from_fp, derive_sk1
from zilant_prime_core.utils.device_fp import get_device_fp


def test_counter_increment(tmp_path, monkeypatch):
    fp = get_device_fp()
    sk0 = derive_sk0_from_fp(fp)
    sk1 = derive_sk1(sk0, b"pwd")
    set_sk1_handle(sk1)
    monkeypatch.setenv("HOME", str(tmp_path))
    init_counter_storage(sk1)
    c0 = get_monotonic_counter()
    c1 = increment_monotonic_counter(sk1)
    assert c1 == c0 + 1
