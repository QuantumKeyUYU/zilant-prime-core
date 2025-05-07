from src.zil import create_zil, unpack_zil

def test_zil_roundtrip():
    data = b"secret data"
    z = create_zil(data, "pw", vdf_iters=10, tries=2, metadata=b"ali")
    pt, _ = unpack_zil(z, "pw")
    assert pt == data

def test_zil_wrong_pass():
    data = b"x"
    z = create_zil(data, "pw", vdf_iters=1, tries=1)
    pt, _ = unpack_zil(z, "bad")
    assert pt is None
