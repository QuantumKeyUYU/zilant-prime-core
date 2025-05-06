import hashlib
from src.vdf import vdf

def test_vdf_zero_iters():
    assert vdf(b'abc', 0) == b'abc'

def test_vdf_one_iter():
    assert vdf(b'abc', 1) == hashlib.sha256(b'abc').digest()
