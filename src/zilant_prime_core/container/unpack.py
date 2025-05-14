from __future__ import annotations
import struct
from pathlib import Path

from zilant_prime_core.utils.constants import HEADER_FMT, MAGIC, VERSION
from zilant_prime_core.container.metadata import deserialize_metadata
from zilant_prime_core.utils.formats import from_b64
from zilant_prime_core.crypto.kdf import derive_key
from zilant_prime_core.crypto.aead import decrypt_aead
from zilant_prime_core.vdf.vdf import verify_posw_sha256, VDFVerificationError

def unpack(container: bytes | str | Path, *, output_dir: str | Path, password: str) -> Path:
    data = (
        Path(container).read_bytes()
        if isinstance(container, (str, Path))
        else container
    )
    magic, ver, mlen, plen, slen = struct.unpack_from(HEADER_FMT, data)
    if magic != MAGIC or ver != VERSION:
        raise ValueError("Invalid container header.")

    off = struct.calcsize(HEADER_FMT)
    meta_blob = data[off : off + mlen]; off += mlen
    proof     = data[off : off + plen]; off += plen
    sig       = data[off : off + slen]; off += slen
    nonce     = data[off : off + 12];   off += 12
    ct_tag    = data[off : ]

    # VDF
    if not verify_posw_sha256(ct_tag, proof, 1):
        raise VDFVerificationError("Bad VDF proof.")

    meta = deserialize_metadata(meta_blob)
    salt = meta.get("salt")
    # salt мог быть base64-строкой
    if isinstance(salt, str):
        salt = from_b64(salt)

    key = derive_key(password, salt)
    plaintext = decrypt_aead(key, nonce, ct_tag)

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / meta["filename"]
    if out_path.exists():
        raise FileExistsError(out_path)
    out_path.write_bytes(plaintext)
    return out_path
