from src.zil import create_zil, unpack_zil

def test_zil_roundtrip():
    data = b"secret data"
    z = create_zil(data, "pw", vdf_iters=10, metadata=b"m")
    plain, meta = unpack_zil(z, "pw")
    assert plain == data and meta == b"m"

def test_zil_wrong_pass():
    z = create_zil(b"x", "pw", vdf_iters=1)
    plain, _ = unpack_zil(z, "wrong")
    assert plain is None

def test_one_shot_behavior():
    data = b"top"
    z = create_zil(data, "pw", vdf_iters=5, one_shot=True)
    first, _ = unpack_zil(z, "pw")
    second, _ = unpack_zil(z, "pw")
    assert first == data
    assert second is None  # повторное вскрытие блокируется
