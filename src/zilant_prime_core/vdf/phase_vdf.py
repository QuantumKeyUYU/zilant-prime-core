import hashlib


class VDFVerificationError(Exception):
    """Ошибка проверки элементарного VDF."""


def generate_elc_vdf(seed: bytes, steps: int) -> bytes:
    if not isinstance(seed, (bytes, bytearray)):
        raise ValueError("Seed must be bytes.")
    if not isinstance(steps, int) or steps <= 0:
        raise ValueError("Steps must be a positive integer.")
    h = seed
    for _ in range(steps):
        h = hashlib.sha256(h).digest()
    return h


def verify_elc_vdf(seed: bytes, steps: int, proof: bytes) -> bool:
    if not isinstance(seed, (bytes, bytearray)):
        raise ValueError("Seed must be bytes.")
    if not isinstance(steps, int) or steps <= 0:
        raise ValueError("Steps must be a positive integer.")
    if not isinstance(proof, (bytes, bytearray)) or len(proof) != hashlib.sha256(b"").digest_size:
        raise ValueError("Proof must be bytes of correct length.")
    return generate_elc_vdf(seed, steps) == proof


def generate_landscape(seed: bytes, steps: int) -> bytes:
    return generate_elc_vdf(seed, steps)


def verify_landscape(seed: bytes, steps: int, proof: bytes) -> bool:
    return verify_elc_vdf(seed, steps, proof)
