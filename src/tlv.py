# src/tlv.py

"""
TLV utilities: Type(1) | Length(2 BE) | Value
Built-in types: 0x01 = MIME, 0x02 = format-version
"""

import struct

from typing import Dict


def encode_tlv(fields: Dict[int, bytes]) -> bytes:
    b = bytearray()
    for t, v in fields.items():
        if not (0 <= t <= 255):
            raise ValueError("TLV type must fit in one byte")
        if len(v) > 0xFFFF:
            raise ValueError("TLV value too long")
        b += bytes([t]) + struct.pack(">H", len(v)) + v
    return bytes(b)


def decode_tlv(buf: bytes) -> Dict[int, bytes]:
    i, out = 0, {}
    while i < len(buf):
        t = buf[i]
        length = struct.unpack(">H", buf[i + 1 : i + 3])[0]
        i += 3
        out[t] = buf[i : i + length]
        i += length
    return out
