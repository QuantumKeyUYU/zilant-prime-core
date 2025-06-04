from __future__ import annotations

__all__ = ["bytes_equal_ct"]


def bytes_equal_ct(a: bytes, b: bytes) -> bool:
    """Compare two byte strings in constant time."""
    if not isinstance(a, (bytes, bytearray)) or not isinstance(b, (bytes, bytearray)):
        raise TypeError("Inputs must be bytes or bytearray")
    if len(a) != len(b):
        return False
    result = 0
    for x, y in zip(a, b, strict=False):
        result |= x ^ y
    return result == 0
