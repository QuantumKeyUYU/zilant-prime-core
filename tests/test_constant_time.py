from zilant_prime_core.utils.constant_time import bytes_equal_ct


def test_bytes_equal_ct_basic():
    assert bytes_equal_ct(b"abc", b"abc")
    assert not bytes_equal_ct(b"abc", b"abd")


def test_bytes_equal_ct_property():
    for a in [b"", b"123", b"foo", b"bar"]:
        for b in [b"", b"123", b"foo", b"bar"]:
            if len(a) == len(b):
                assert bytes_equal_ct(a, b) == (a == b)
            else:
                assert not bytes_equal_ct(a, b)
