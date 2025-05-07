"""
TLV-утилиты (Type:1 байт | Length:2 байта | Value)
type:   0x01 = content‑type (MIME)
        0x02 = format‑version (ASCII)
        0x80..0xFF = пользовательские
"""
import struct
from typing import Dict, Tuple

def encode_tlv(fields: Dict[int, bytes]) -> bytes:
    buf = bytearray()
    for t, v in fields.items():
        if not (0 <= t <= 255):
            raise ValueError("TLV type must fit in 1 byte")
        if len(v) > 0xFFFF:
            raise ValueError("TLV value too long")
        buf += bytes([t])
        buf += struct.pack(">H", len(v))
        buf += v
    return bytes(buf)

def decode_tlv(buf: bytes) -> Dict[int, bytes]:
    idx = 0
    out: Dict[int, bytes] = {}
    while idx < len(buf):
        t = buf[idx]
        l = struct.unpack(">H", buf[idx + 1 : idx + 3])[0]
        idx += 3
        out[t] = buf[idx : idx + l]
        idx += l
    return out
