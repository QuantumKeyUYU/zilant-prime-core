import hashlib

def vdf(x: bytes, n: int) -> bytes:
    h = x
    for _ in range(n):
        h = hashlib.sha256(h).digest()
    return h
