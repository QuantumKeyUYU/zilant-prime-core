import hashlib
from src.vdf import vdf

def test_vdf_correctness():
    h = vdf(b"zero", 5)
    # вручную 5 sha256
    expected = b"zero"
    for _ in range(5):
        expected = hashlib.sha256(expected).digest()
    assert h == expected
