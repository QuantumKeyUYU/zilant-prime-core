import hashlib

def vdf(x: bytes, N: int) -> bytes:
    """
    Непараллелируемая задержка: N SHA256 подряд.
    """
    h = x
    for _ in range(N):
        h = hashlib.sha256(h).digest()
    return h
