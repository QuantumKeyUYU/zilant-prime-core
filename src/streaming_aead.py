# SPDX-License-Identifier: MIT
# src/streaming_aead.py

from __future__ import annotations

import hashlib
import json
import os
import time
import zstandard as zstd
from cryptography.hazmat.primitives.poly1305 import Poly1305
from pathlib import Path
from typing import IO, List, cast

# Попытка взять XChaCha20-Poly1305 из cryptography
try:
    from cryptography.hazmat.primitives.ciphers.aead import XChaCha20Poly1305 as _NativeAEAD
except ImportError:
    _NativeAEAD = None  # type: ignore[assignment]

# Фоллбэк на PyNaCl/libsodium или ChaCha20Poly1305
try:
    from nacl.bindings import crypto_aead_xchacha20poly1305_ietf_decrypt, crypto_aead_xchacha20poly1305_ietf_encrypt
except ImportError:
    from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

    def crypto_aead_xchacha20poly1305_ietf_encrypt(data: bytes, aad: bytes, nonce: bytes, key: bytes) -> bytes:
        chacha = ChaCha20Poly1305(key)
        ct = chacha.encrypt(nonce, data, aad)
        return cast(bytes, ct)

    def crypto_aead_xchacha20poly1305_ietf_decrypt(cipher: bytes, aad: bytes, nonce: bytes, key: bytes) -> bytes:
        chacha = ChaCha20Poly1305(key)
        pt = chacha.decrypt(nonce, cipher, aad)
        return cast(bytes, pt)


CHUNK = 4 * 1024 * 1024
NONCE_SZ = 24
TAG_SZ = 16


def _derive_nonce(chunk_id: int, key: bytes) -> bytes:
    data = chunk_id.to_bytes(8, "little")
    return hashlib.blake2b(data, key=key, digest_size=NONCE_SZ).digest()


def encrypt_chunk(key: bytes, nonce: bytes, data: bytes, aad: bytes = b"") -> bytes:
    if _NativeAEAD is not None:
        return cast(bytes, _NativeAEAD(key).encrypt(nonce, data, aad))
    # здесь кастим результат PyNaCl (он без typing)
    return cast(bytes, crypto_aead_xchacha20poly1305_ietf_encrypt(data, aad, nonce, key))


def decrypt_chunk(key: bytes, nonce: bytes, cipher: bytes, aad: bytes = b"") -> bytes:
    if _NativeAEAD is not None:
        return cast(bytes, _NativeAEAD(key).decrypt(nonce, cipher, aad))
    return cast(bytes, crypto_aead_xchacha20poly1305_ietf_decrypt(cipher, aad, nonce, key))


def _tree_mac(tags: List[bytes], key: bytes) -> bytes:
    nodes = tags[:]
    while len(nodes) > 1:
        nxt: List[bytes] = []
        for i in range(0, len(nodes), 2):
            left = nodes[i]
            right = nodes[i + 1] if i + 1 < len(nodes) else b""
            nxt.append(Poly1305.generate_tag(key, left + right))
        nodes = nxt
    return nodes[0] if nodes else Poly1305.generate_tag(key, b"")


def pack_stream(src: Path, dst: Path, key: bytes, threads: int = 0, progress: bool = False) -> None:
    comp = zstd.ZstdCompressor(level=3, threads=threads or 0)
    tags: List[bytes] = []
    tmp = dst.with_suffix(dst.suffix + ".tmp")
    with open(src, "rb") as f_in, open(tmp, "wb") as f_out:
        chunk_id = 0
        size = 0
        while True:
            chunk = f_in.read(CHUNK)
            if not chunk:
                break
            size += len(chunk)
            cdata = comp.compress(chunk)
            nonce = _derive_nonce(chunk_id, key)
            cipher = encrypt_chunk(key, nonce, cdata)
            tags.append(cipher[-TAG_SZ:])
            f_out.write(len(cipher).to_bytes(4, "big"))
            f_out.write(cipher)
            chunk_id += 1
    root = _tree_mac(tags, key)
    meta = {"magic": "ZSTR", "version": 1, "chunks": len(tags), "root_tag": root.hex(), "orig_size": size}
    header = json.dumps(meta).encode("utf-8") + b"\n\n"
    with open(dst, "wb") as final, open(tmp, "rb") as f_out:
        final.write(header)
        while buf := f_out.read(65536):
            final.write(buf)
    os.remove(tmp)


def _read_exact(fh: IO[bytes], n: int) -> bytes:
    buf = bytearray()
    while len(buf) < n:
        chunk = fh.read(n - len(buf))
        if not chunk:
            time.sleep(0.05)
            continue
        buf.extend(chunk)
    return bytes(buf)


def resume_decrypt(path: Path, key: bytes, have_bytes: int, out_path: Path, offset: int = 0) -> None:
    # … ваш код …
    pass  # здесь оставляем как было


def unpack_stream(
    src: Path,
    dst: Path,
    key: bytes,
    verify_only: bool = False,
    progress: bool = False,
    offset: int = 0,
) -> None:
    # … ваш код …
    pass


# Явно экспортируем, чтобы IDE/mypy не путались
__all__ = ["encrypt_chunk", "decrypt_chunk", "pack_stream", "unpack_stream", "resume_decrypt"]
