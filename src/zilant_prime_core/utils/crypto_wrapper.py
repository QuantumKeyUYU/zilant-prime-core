# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

"""ctypes wrapper for crypto_core.so"""

from __future__ import annotations

import ctypes
from pathlib import Path

LIB_PATH = Path(__file__).with_name("crypto_core.so")

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
