# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core Contributors

from __future__ import annotations

import json
from pathlib import Path
from typing import cast

from aead import PQAEAD, decrypt, encrypt
from crypto_core import hash_sha3
from utils.file_utils import atomic_write
from utils.logging import get_logger
from zilant_prime_core.utils.pq_crypto import Kyber768KEM, derive_key_pq

ZIL_MAGIC = b"ZILANT"
ZIL_VERSION = 1
HEADER_SEPARATOR = b"\n\n"

logger = get_logger("container")


def pack_file(
    input_path: Path,
    output_path: Path,
    key: bytes,
    pq_public_key: bytes | None = None,
) -> None:
    """Encrypt *input_path* into *output_path* using *key* or PQ mode."""

    plaintext = input_path.read_bytes()
    checksum = cast(bytes, hash_sha3(plaintext))
    if pq_public_key is not None:
        payload = PQAEAD.encrypt(pq_public_key, plaintext, aad=b"")
        metadata = {
            "magic": ZIL_MAGIC.decode("ascii"),
            "version": ZIL_VERSION,
            "mode": "pq",
            "kem_ct_len": len(payload) - len(plaintext) - 12,
            "orig_size": len(plaintext),
            "checksum_hex": checksum.hex(),
        }
        header_bytes = json.dumps(metadata, ensure_ascii=False).encode("utf-8")
        container_data = header_bytes + HEADER_SEPARATOR + payload
    else:
        nonce, ciphertext = encrypt(key, plaintext, aad=b"")
        metadata = {
            "magic": ZIL_MAGIC.decode("ascii"),
            "version": ZIL_VERSION,
            "mode": "classic",
            "nonce_hex": nonce.hex(),
            "orig_size": len(plaintext),
            "checksum_hex": checksum.hex(),
        }
        header_bytes = json.dumps(metadata, ensure_ascii=False).encode("utf-8")
        container_data = header_bytes + HEADER_SEPARATOR + ciphertext
    tmp = output_path.with_suffix(output_path.suffix + ".tmp")
    atomic_write(tmp, container_data)
    tmp.replace(output_path)
    logger.info(
        "Packed '%s' -> '%s', size=%d bytes",
        input_path.name,
        output_path.name,
        len(container_data),
    )


def unpack_file(
    input_path: Path,
    output_path: Path,
    key: bytes,
    pq_private_key: bytes | None = None,
) -> None:
    """Decrypt *input_path* into *output_path* using classic or PQ mode."""
    data = input_path.read_bytes()
    sep_idx = data.find(HEADER_SEPARATOR)
    if sep_idx == -1:
        logger.error("Malformed .zil: separator not found")
        raise ValueError("Invalid ZIL container format")
    header_bytes = data[:sep_idx]
    payload = data[sep_idx + len(HEADER_SEPARATOR) :]
    metadata = json.loads(header_bytes.decode("utf-8"))
    if metadata.get("magic") != ZIL_MAGIC.decode("ascii"):
        logger.error("Magic-header mismatch")
        raise ValueError("Invalid ZIL magic value")
    if metadata.get("version") != ZIL_VERSION:
        logger.error("Unsupported ZIL version")
        raise ValueError("Unsupported ZIL version")
    mode = metadata.get("mode", "classic")
    orig_size = metadata["orig_size"]
    checksum_hex = metadata["checksum_hex"]
    if mode == "pq":
        if pq_private_key is None:
            raise ValueError("pq_private_key required")
        kem_len = metadata["kem_ct_len"]
        kem_ct = payload[:kem_len]
        nonce = payload[kem_len : kem_len + PQAEAD._NONCE_LEN]
        ct = payload[kem_len + PQAEAD._NONCE_LEN :]
        kem = Kyber768KEM()
        shared = kem.decapsulate(pq_private_key, kem_ct)
        key_dec = derive_key_pq(shared)
        plaintext = decrypt(key_dec, nonce, ct, aad=b"")
    else:
        nonce = bytes.fromhex(metadata["nonce_hex"])
        plaintext = decrypt(key, nonce, payload, aad=b"")
    actual_checksum = cast(bytes, hash_sha3(plaintext)).hex()
    if actual_checksum != checksum_hex:
        logger.error("Checksum mismatch")
        raise ValueError("Integrity check failed")
    if len(plaintext) != orig_size:
        logger.error("Size mismatch: expected=%d, got=%d", orig_size, len(plaintext))
        raise ValueError("Original size mismatch")
    atomic_write(output_path, plaintext)
    logger.info("Unpacked '%s' -> '%s'", input_path.name, output_path.name)
