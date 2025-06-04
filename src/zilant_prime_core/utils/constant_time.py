from __future__ import annotations

__all__ = ["bytes_equal_ct"]


def bytes_equal_ct(a: bytes, b: bytes) -> bool:
    """Compare two byte strings in constant time."""
    if len(a) != len(b):
        return False
    result = 0
    for x, y in zip(a, b, strict=False):
        result |= x ^ y
    return result == 0
