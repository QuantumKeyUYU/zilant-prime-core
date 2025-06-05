from zilant_prime_core.utils.device_fp import get_device_fp


def test_device_fp_length():
    fp = get_device_fp()
    assert isinstance(fp, bytes)
    assert len(fp) == 12 * 32
