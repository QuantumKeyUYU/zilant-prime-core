from src.aead import encrypt, decrypt

def test_aead_roundtrip():
    key = b"\x00" * 32
    pt  = b"hello"
    md  = b"meta"
    nonce, blob = encrypt(key, pt, md)
    out = decrypt(key, nonce, blob, md)
    assert out == pt
