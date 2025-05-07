import struct
from typing import Tuple
from cryptography.exceptions import InvalidTag

from .kdf import derive_key
from .vdf import compute_vdf, verify_vdf
from .aead import encrypt, decrypt

MAGIC = b'ZIL1'  # 4 байта "магии" для быстрой проверки формата

def create_zil(
    data: bytes,
    passphrase: str,
    vdf_iters: int,
    tries: int,
    metadata: bytes = b''
) -> bytes:
    """
    Упаковывает данные в формат ZIL:
    MAGIC (4) |
    salt (32) |
    tries (4 BE) |
    vdf_iters (4 BE) |
    proof (32) |
    nonce (12) |
    metadata_length (4 BE) |
    metadata (…) |
    ciphertext_and_tag (…)
    """
    key, salt = derive_key(passphrase)
    proof = compute_vdf(tries, vdf_iters)
    # связываем proof + metadata как AD, чтобы при любом изменении метаданных шифрование ломалось
    nonce, ct = encrypt(key, data, proof + metadata)

    buf = bytearray()
    buf += MAGIC
    buf += salt
    buf += struct.pack(">I", tries)
    buf += struct.pack(">I", vdf_iters)
    buf += proof
    buf += nonce
    buf += struct.pack(">I", len(metadata))
    buf += metadata
    buf += ct
    return bytes(buf)

def unpack_zil(zil_bytes: bytes, passphrase: str) -> Tuple[bytes | None, bytes | None]:
    """
    Распаковывает ZIL. Если что-то не так (магия, VDF, AD-тег), возвращает (None, None).
    Иначе — (plaintext, metadata).
    """
    try:
        idx = 0
        if zil_bytes[:4] != MAGIC:
            return None, None
        idx += 4

        salt = zil_bytes[idx:idx+32]; idx += 32
        tries = struct.unpack(">I", zil_bytes[idx:idx+4])[0]; idx += 4
        vdf_iters = struct.unpack(">I", zil_bytes[idx:idx+4])[0]; idx += 4
        proof = zil_bytes[idx:idx+32]; idx += 32

        # проверяем VDF-доказательство
        if not verify_vdf(proof, tries, vdf_iters):
            return None, None

        nonce = zil_bytes[idx:idx+12]; idx += 12
        meta_len = struct.unpack(">I", zil_bytes[idx:idx+4])[0]; idx += 4
        metadata = zil_bytes[idx:idx+meta_len]; idx += meta_len
        ciphertext = zil_bytes[idx:]

        key, _ = derive_key(passphrase, salt)
        plaintext = decrypt(key, nonce, ciphertext, proof + metadata)
        return plaintext, metadata

    except (InvalidTag, Exception):
        # любая ошибка разбора или проверки тегов = неверный ZIL или пароль
        return None, None
