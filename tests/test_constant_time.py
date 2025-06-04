import pytest
from zilant_prime_core.utils.constant_time import bytes_equal_ct


@pytest.mark.parametrize(
    "a,b,expected",
    [
        (b"", b"", True),
        (b"\x00\xff", b"\x00\xff", True),
        (b"\x00\xff", b"\x00\xfe", False),
        (b"abc", b"abcd", False),
    ],
)
def test_bytes_equal_ct(a, b, expected):
    assert bytes_equal_ct(a, b) is expected


def test_bytes_equal_ct_invalid_type():
    with pytest.raises(TypeError):
        bytes_equal_ct("string", b"bytes")
