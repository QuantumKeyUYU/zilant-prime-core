import struct
from .kdf import derive_key
from .vdf import vdf
from .aead import encrypt, decrypt

MAGIC = b"ZIL1"

def create_zil(
    data: bytes,
    passphrase: str,
    vdf_iters: int,
    tries: int,
    metadata: bytes = b""
) -> bytes:
    # 1) KDF
    key, salt = derive_key(passphrase)

    # 2) VDF barrier state
    vstate = vdf(key + metadata, vdf_iters)

    # 3) AEAD
    nonce, ct = encrypt(key, data, metadata)

    # 4) Phase fingerprint & watermark
    fp = __import__("hashlib").sha256(vstate + key + metadata).digest()[:16]

    # 5) Собираем .zil контейнер
    header = (
        MAGIC +                                    # 4B
        struct.pack("B", 1) +                      # version=1
        struct.pack("B", tries) +                  # tries_left
        struct.pack(">I", vdf_iters) +             # 4B big-endian
        struct.pack(">Q", int(__import__("time").time())) +  # timestamp 8B
        salt +                                     # 32B
        nonce +                                    # 12B
        fp                                         # 16B
    )
    return header + ct

def unpack_zil(blob: bytes, passphrase: str, metadata: bytes = b"") -> tuple[bytes, bytes]:
    # Парсим шапку
    (
        magic, version, tries_left, vdf_iters,
        timestamp, salt, nonce, fp
    ) = (
        blob[0:4], blob[4], blob[5], struct.unpack(">I", blob[6:10])[0],
        struct.unpack(">Q", blob[10:18])[0], blob[18:50],
        blob[50:62], blob[62:78]
    )
    if magic != MAGIC or version != 1:
        raise ValueError("Invalid .zil format")

    # KDF
    from .kdf import derive_key as _kdf
    key, _ = _kdf(passphrase)

    # VDF
    vstate = vdf(key + metadata, vdf_iters)

    # Проверяем watermark
    expected_fp = __import__("hashlib").sha256(vstate + key + metadata).digest()[:16]
    if expected_fp != fp:
        return None, metadata  # zero-feedback

    # AEAD
    ct = blob[78:]
    try:
        pt = decrypt(key, nonce, ct, metadata)
    except:
        return None, metadata

    # self-destruct условия можно здесь
    return pt, metadata
