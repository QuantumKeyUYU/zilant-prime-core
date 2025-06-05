# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

"""Wrapper for ``crypto_core.so`` with Python fallback."""

from __future__ import annotations

import ctypes
import hashlib
import hmac
from pathlib import Path
from typing import Optional

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

LIB_PATH = Path(__file__).with_name("crypto_core.so")

_sk0: Optional[bytes] = None
_sk1: Optional[bytes] = None

if LIB_PATH.exists():
    lib = ctypes.CDLL(str(LIB_PATH))

    lib.derive_sk0_from_fp.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_uint8)]
    lib.derive_sk0_from_fp.restype = ctypes.c_int

    lib.derive_sk1.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_uint8)]
    lib.derive_sk1.restype = ctypes.c_int

    lib.get_sk_bytes.argtypes = [ctypes.c_int, ctypes.c_void_p]
    lib.get_sk_bytes.restype = ctypes.c_int

    lib.release_sk.argtypes = [ctypes.c_int]
    lib.release_sk.restype = None

    def derive_sk0_from_fp(fp: bytes) -> int:
        handle = ctypes.c_uint8()
        res = lib.derive_sk0_from_fp(fp, len(fp), ctypes.byref(handle))
        if res != 1:
            raise RuntimeError("derive_sk0_from_fp failed")
        return int(handle.value)

    def derive_sk1(sk0_handle: int, user_secret: bytes) -> int:
        handle = ctypes.c_uint8()
        res = lib.derive_sk1(int(sk0_handle), user_secret, len(user_secret), ctypes.byref(handle))
        if res != 1:
            raise RuntimeError("derive_sk1 failed")
        return int(handle.value)

    def get_sk_bytes(handle: int) -> bytes:
        buf = (ctypes.c_uint8 * 32)()
        res = lib.get_sk_bytes(int(handle), buf)
        if res != 1:
            raise RuntimeError("get_sk_bytes failed")
        return bytes(buf)

    def release_sk(handle: int) -> None:
        lib.release_sk(int(handle))

else:

    def derive_sk0_from_fp(fp: bytes) -> int:
        """Derive SK0 using HKDF in pure Python."""
        global _sk0
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"ZILANT_SK0_SALT__",
            info=b"ZILANT_INFO_SK0_",
        )
        _sk0 = hkdf.derive(fp)
        return 1

    def derive_sk1(sk0_handle: int, user_secret: bytes) -> int:
        """Derive SK1 from SK0 and user secret in pure Python."""
        global _sk1
        if sk0_handle != 1 or _sk0 is None:
            raise RuntimeError("sk0 not derived")
        salt1 = hmac.new(_sk0, user_secret, hashlib.sha256).digest()
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt1,
            info=b"ZILANT_INFO_SK1_",
        )
        _sk1 = hkdf.derive(_sk0)
        return 1

    def get_sk_bytes(handle: int) -> bytes:
        if handle != 1 or _sk1 is None:
            raise RuntimeError("sk1 not derived")
        return _sk1

    def release_sk(handle: int) -> None:
        global _sk0, _sk1
        _sk0 = None
        _sk1 = None
