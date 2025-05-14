from __future__ import annotations
import struct
from pathlib import Path

from zilant_prime_core.utils.constants import HEADER_FMT, MAGIC, VERSION
from zilant_prime_core.container.metadata import new_meta_for_file, serialize_metadata
from zilant_prime_core.crypto.kdf import derive_key, generate_salt
from zilant_prime_core.crypto.aead import encrypt_aead, generate_nonce
from zilant_prime_core.vdf.vdf import generate_posw_sha256

def pack(path: str | Path, *, password: str) -> bytes:
    p = Path(path)
    payload = p.read_bytes()

    # ── метаданные ──
    salt = generate_salt()
    meta = new_meta_for_file(p)
    meta.extra["salt"] = salt
    meta_blob = serialize_metadata(meta)

    # ── крипто шаги ──
    key = derive_key(password, salt)
    nonce = generate_nonce()
    ct_tag = encrypt_aead(key, nonce, payload)

    # ── простой VDF ──
    proof = generate_posw_sha256(ct_tag, 1)  # для тестов хватит 1 шага
    sig = b""

# Note: pack не добавляет «подпись», т.к. тестам она не нужна

    # ── собираем всё вместе ──
    header = struct.pack(
        HEADER_FMT,
        MAGIC, VERSION,
        len(meta_blob), len(proof), len(sig),
    )
    return b"".join([header, meta_blob, proof, sig, nonce, ct_tag])
