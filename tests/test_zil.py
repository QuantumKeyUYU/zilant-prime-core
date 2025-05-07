from src.zil import create_zil, unpack_zil

def test_zil_roundtrip():
    data = b"secret data"
    passphrase = "pw"
    vdf_iters = 10
    metadata = b"ali"

    z = create_zil(data, passphrase, vdf_iters, metadata=metadata)
    plaintext, meta_out = unpack_zil(z, passphrase)

    assert plaintext == data
    assert meta_out == metadata

def test_zil_wrong_pass():
    data = b"x"
    passphrase = "pw"
    wrong_passphrase = "wrong_pw"
    vdf_iters = 1

    z = create_zil(data, passphrase, vdf_iters)
    plaintext, meta_out = unpack_zil(z, wrong_passphrase)

    assert plaintext is None
    assert meta_out is None
