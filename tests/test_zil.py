from src.zil import create_zil, unpack_zil

# --- базовый круговой тест ---
def test_zil_roundtrip():
    z = create_zil(b"secret", "pw", 10)
    plain, meta = unpack_zil(z, "pw")
    assert plain == b"secret"
    assert meta == {}

# --- неверный пароль ---
def test_zil_wrong_pass():
    z = create_zil(b"hi", "pw", 2)
    plain, _ = unpack_zil(z, "wrong_pw")
    assert plain is None

# --- one‑shot контейнер ---
def test_one_shot_behavior():
    z = create_zil(b"one", "pw", 5, one_shot=True)
    first, _ = unpack_zil(z, "pw")
    second, _ = unpack_zil(z, "pw")
    assert first == b"one"
    assert second is None

# --- TLV‑метаданные round‑trip ---
def test_tlv_roundtrip():
    meta_in = {0x01: b"text/plain", 0x02: b"3.1"}
    z = create_zil(b"hello", "pw", 7, metadata=meta_in)
    plain, meta_out = unpack_zil(z, "pw")
    assert plain == b"hello"
    assert meta_out == meta_in
