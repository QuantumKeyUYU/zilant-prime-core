from zil import create_zil, unpack_zil

def test_roundtrip_basic():
    z = create_zil(b"secret", "pw", 6)
    pt, meta = unpack_zil(z, "pw")
    assert pt == b"secret" and meta == {}

def test_wrong_pass():
    z = create_zil(b"x", "pw", 3)
    pt, _ = unpack_zil(z, "bad")
    assert pt is None

def test_one_shot():
    z = create_zil(b"one", "pw", 4, one_shot=True)
    assert unpack_zil(z, "pw")[0] == b"one"
    assert unpack_zil(z, "pw")[0] is None

def test_tlv_meta():
    meta_in = {0x01: b"text/plain", 0x02: b"3.1"}
    z = create_zil(b"hello", "pw", 5, metadata=meta_in)
    pt, meta_out = unpack_zil(z, "pw")
    assert pt == b"hello" and meta_out == meta_in
