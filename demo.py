from src.kdf import derive_key
from src.vdf import vdf
from src.aead import encrypt, decrypt
from src.zil import create_zil, unpack_zil

# 1) KDF
k, s = derive_key("foo")
print("KDF OK:", len(k), len(s))

# 2) VDF
h = vdf(b"hello", 5)
print("VDF OK:", isinstance(h, bytes))

# 3) AEAD
nonce, ct = encrypt(k, b"plain", b"meta")
pt = decrypt(k, nonce, ct, b"meta")
print("AEAD OK:", pt)

# 4) .zil
cont = create_zil(b"data", "foo", vdf_iters=10, tries=2, metadata=b"demo.txt")
pt2, _ = unpack_zil(cont, "foo", metadata=b"demo.txt")
print(".zil OK:", pt2)
