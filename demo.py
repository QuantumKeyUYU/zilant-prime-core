from src.kdf import derive_key
from src.vdf import vdf
from src.aead import encrypt, decrypt
from src.zil import create_zil, unpack_zil

if __name__ == "__main__":
    print("KDF OK:", *map(len, derive_key("foo")[0:2]))
    print("VDF OK:", isinstance(vdf(b"hello", 5), bytes))
    key, _ = derive_key("bar")
    nonce, ct = encrypt(key, b"plain", b"meta")
    print("AEAD OK:", decrypt(key, nonce, ct, b"meta"))
    z = create_zil(b"secret", "pw", vdf_iters=10, tries=2, metadata=b"md")
    pt, _ = unpack_zil(z, "pw", metadata=b"md")
    print(".zil OK:", pt)
