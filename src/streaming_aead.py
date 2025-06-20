from __future__ import annotations

import hashlib
import importlib
import json
import os
import sys
import types
import zstandard as zstd
from json import JSONDecodeError
from pathlib import Path
from typing import IO, Any, List, cast
from zstandard import ZstdError

try:
    from cryptography.exceptions import InvalidTag
    from cryptography.hazmat.primitives.ciphers.aead import XChaCha20Poly1305 as _NativeAEAD
except ImportError:  # pragma: no cover – optional dep
    _NativeAEAD = None  # type: ignore[assignment]
    InvalidTag = Exception  # fallback

from cryptography.hazmat.primitives.poly1305 import Poly1305

# ───────────────────────── constants ────────────────────────────
CHUNK = 4 * 1024 * 1024
TAG_SZ = 16
NONCE_SZ = 24


# ───────────────────── helper: nacl.bindings shim ───────────────
def _safe_get_nacl_bindings() -> types.ModuleType:
    """Return a *hashable* module object for ``nacl.bindings``."""
    bindings = importlib.import_module("nacl.bindings")
    if not isinstance(bindings, types.ModuleType):
        fixed = types.ModuleType("nacl.bindings")
        fixed.__dict__.update(bindings.__dict__)
        sys.modules["nacl.bindings"] = fixed
        bindings = fixed
    return bindings


# ──────────────────────── crypto helpers ────────────────────────
def _derive_nonce(chunk_id: int, key: bytes) -> bytes:
    return hashlib.blake2b(chunk_id.to_bytes(8, "little"), key=key, digest_size=NONCE_SZ).digest()


def encrypt_chunk(
    key: bytes,
    nonce: bytes,
    data: bytes,
    aad: bytes | None = b"",
) -> bytes:
    if _NativeAEAD is not None:
        return cast(bytes, _NativeAEAD(key).encrypt(nonce, data, aad or b""))
    bindings = _safe_get_nacl_bindings()
    return cast(
        bytes,
        bindings.crypto_aead_xchacha20poly1305_ietf_encrypt(  # type: ignore[attr-defined,no-any-return]
            data,
            aad,
            nonce,
            key,
        ),
    )


def decrypt_chunk(
    key: bytes,
    nonce: bytes,
    cipher: bytes,
    aad: bytes | None = b"",
) -> bytes:
    if _NativeAEAD is not None:
        return cast(bytes, _NativeAEAD(key).decrypt(nonce, cipher, aad or b""))
    bindings = _safe_get_nacl_bindings()
    return cast(
        bytes,
        bindings.crypto_aead_xchacha20poly1305_ietf_decrypt(  # type: ignore[attr-defined,no-any-return]
            cipher,
            aad,
            nonce,
            key,
        ),
    )


# ────────────────────────── MAC tree ────────────────────────────
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


# ───────────────────────── packing side ──────────────────────────
def pack_stream(src: Path, dst: Path, key: bytes, threads: int = 0, progress: bool = False) -> None:  # noqa: D401,E501
    comp = zstd.ZstdCompressor(level=3, threads=threads or 0)
    tags: List[bytes] = []
    tmp = dst.with_suffix(dst.suffix + ".tmp")
    size = 0

    with open(src, "rb") as fin, open(tmp, "wb") as tmp_out:
        cid = 0
        while chunk := fin.read(CHUNK):
            size += len(chunk)
            cdata = comp.compress(chunk)
            nonce = _derive_nonce(cid, key)
            cipher = encrypt_chunk(key, nonce, cdata)
            tags.append(cipher[-TAG_SZ:])
            tmp_out.write(len(cipher).to_bytes(4, "big") + cipher)
            cid += 1

    header = (
        json.dumps(
            {
                "magic": "ZSTR",
                "version": 1,
                "chunks": len(tags),
                "root_tag": _tree_mac(tags, key).hex(),
                "orig_size": size,
            }
        ).encode()
        + b"\n\n"
    )

    with open(dst, "wb") as final, open(tmp, "rb") as tmp_in:
        final.write(header)
        while buf := tmp_in.read(1 << 16):
            final.write(buf)
    os.remove(tmp)


# ──────────────────────── I/O utilities ─────────────────────────
def _read_exact(fh: IO[bytes], n: int) -> bytes:
    buf = bytearray()
    while len(buf) < n:
        chunk = fh.read(n - len(buf))
        if not chunk:
            raise EOFError("truncated stream")
        buf.extend(chunk)
    return bytes(buf)


def _load_header(fh: IO[bytes]) -> dict[str, Any]:
    hdr = bytearray()
    while not hdr.endswith(b"\n\n"):
        b = fh.read(1)
        if not b:
            raise ValueError("truncated header")
        hdr.extend(b)
    try:
        return cast(dict[str, Any], json.loads(hdr[:-2].decode()))
    except JSONDecodeError:
        raise ValueError("truncated header") from None


# ─────────────────── resume-decrypt (≥ 51 %) ────────────────────
def resume_decrypt(
    path: Path,
    key: bytes,
    have_bytes: int,
    out_path: Path,
    offset: int = 0,
) -> None:
    total = os.path.getsize(path)
    if have_bytes < total * 0.51:
        raise ValueError("insufficient data for resume")

    with open(path, "rb") as fin:
        meta = _load_header(fin)
        root_tag = bytes.fromhex(meta["root_tag"])
        chunks = meta["chunks"]

        tags: List[bytes] = []
        pos = fin.tell()

        with open(out_path, "wb") as fout:
            for cid in range(chunks):
                clen = int.from_bytes(_read_exact(fin, 4), "big")
                cipher = _read_exact(fin, clen)
                pos += 4 + clen

                tags.append(cipher[-TAG_SZ:])
                nonce = _derive_nonce(cid, key)

                # catch decryption/decompression issues
                try:
                    plain = decrypt_chunk(key, nonce, cipher)
                    data = zstd.decompress(plain)
                except (InvalidTag, ZstdError, Exception):
                    raise ValueError("MAC mismatch")

                # re-encrypt consistency check – should never fail in normal flow
                if encrypt_chunk(key, nonce, plain) != cipher:  # pragma: no cover
                    raise ValueError("MAC mismatch")  # pragma: no cover

                if pos >= offset:
                    fout.write(data)

    # final tree-MAC verification (only when 100 % bytes available)
    if have_bytes >= total and _tree_mac(tags, key) != root_tag:  # pragma: no cover
        raise ValueError("MAC mismatch")  # pragma: no cover


# ───────────────────────── full unpack ──────────────────────────
def unpack_stream(
    src: Path,
    dst: Path,
    key: bytes,
    verify_only: bool = False,
    progress: bool = False,
    offset: int = 0,
) -> None:
    with open(src, "rb") as fin:
        meta = _load_header(fin)
        root_tag = bytes.fromhex(meta["root_tag"])
        chunks = meta["chunks"]

        tags: List[bytes] = []
        pos = fin.tell()
        out_fh = None if verify_only else open(dst, "wb")

        try:
            for cid in range(chunks):
                clen = int.from_bytes(_read_exact(fin, 4), "big")
                cipher = _read_exact(fin, clen)
                tags.append(cipher[-TAG_SZ:])
                nonce = _derive_nonce(cid, key)

                try:
                    plain = decrypt_chunk(key, nonce, cipher)
                    data = zstd.decompress(plain)
                except (InvalidTag, ZstdError):
                    raise ValueError("MAC mismatch") from None

                if encrypt_chunk(key, nonce, plain) != cipher:
                    raise ValueError("MAC mismatch")

                if out_fh and pos >= offset:
                    out_fh.write(data)
                pos += 4 + clen
        finally:
            if out_fh:
                out_fh.close()

        if _tree_mac(tags, key) != root_tag:
            raise ValueError("MAC mismatch")
