from __future__ import annotations

"""Post-quantum and hybrid cryptography helpers."""

import os
from typing import Tuple, cast

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

from zilant_prime_core.utils.pq_crypto import HybridKEM


def hybrid_encrypt(
    recipient_pubkey: Tuple[bytes, bytes],
    plaintext: bytes,
    aad: bytes = b"",
) -> Tuple[bytes, bytes]:
    """Encrypt ``plaintext`` for ``recipient_pubkey`` using hybrid HPKE."""
    kem = HybridKEM()
    ct_pq, _ss_pq, epk, _ss_x, shared = kem.encapsulate(recipient_pubkey)
    nonce = os.urandom(12)
    ct = ChaCha20Poly1305(shared).encrypt(nonce, plaintext, aad)
    enc = ct_pq + epk + nonce
    return enc, ct


def hybrid_decrypt(
    private_key: Tuple[bytes, bytes],
    enc: bytes,
    ciphertext: bytes,
    aad: bytes = b"",
) -> bytes:
    """Decrypt ``ciphertext`` produced by :func:`hybrid_encrypt`."""
    kem = HybridKEM()
    ct_len = len(enc) - 44  # kyber_ct || epk(32) || nonce(12)
    ct_pq = enc[:ct_len]
    epk = enc[ct_len : ct_len + 32]
    nonce = enc[ct_len + 32 :]
    shared = kem.decapsulate(private_key, (ct_pq, epk, b""))
    return cast(bytes, ChaCha20Poly1305(shared).decrypt(nonce, ciphertext, aad))


try:  # pragma: no cover - optional dependency
    from pqclean.branchfree import dilithium3 as dilithium3
except Exception:  # pragma: no cover - optional dependency
    try:
        from pqclean import dilithium3 as dilithium3  # type: ignore
    except Exception:  # pragma: no cover - optional dependency
        dilithium3 = None  # type: ignore


def dual_sign(message: bytes, ed25519_sk: bytes, dilithium3_sk: bytes) -> bytes:
    """Return Ed25519 || Dilithium3 signature."""
    ed_sig = ed25519.Ed25519PrivateKey.from_private_bytes(ed25519_sk).sign(message)
    if dilithium3 is None:
        raise RuntimeError("Dilithium3 not installed")
    pq_sig = cast(bytes, dilithium3.sign(message, dilithium3_sk))  # type: ignore[no-any-return]
    return cast(bytes, ed_sig + pq_sig)


def dual_verify(
    message: bytes,
    signature: bytes,
    ed25519_pk: bytes,
    dilithium3_pk: bytes,
) -> bool:
    """Verify a signature produced by :func:`dual_sign`."""
    if len(signature) < 64:
        return False
    sig_ed = signature[:64]
    sig_pq = signature[64:]
    try:
        ed25519.Ed25519PublicKey.from_public_bytes(ed25519_pk).verify(sig_ed, message)
    except Exception:
        return False
    if dilithium3 is None:
        return False
    try:
        return bool(dilithium3.verify(message, sig_pq, dilithium3_pk))  # type: ignore[no-any-return]
    except Exception:
        return False
