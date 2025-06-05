import os
import struct
import time
import uuid
from dataclasses import dataclass

from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

from .crypto_core import get_sk_from_handle
from .device_fp import get_device_fp


@dataclass
class DecryptedShard:
    shard_key: bytes
    shard_id: uuid.UUID
    usage_counter: int
    wallclock_nonce: int


def _hmac(key: bytes, data: bytes) -> bytes:
    h = hmac.HMAC(key, hashes.SHA256())
    h.update(data)
    return h.finalize()


def generate_shard(sk1_handle: int) -> bytes:
    sk1 = get_sk_from_handle(sk1_handle)
    shard_key = os.urandom(32)
    shard_id = uuid.uuid4()
    usage_counter = 0
    wallclock_nonce = int(time.time() // 300)
    device_fp = get_device_fp()
    fp_h = _hmac(sk1, shard_id.bytes + device_fp)
    header = shard_id.bytes + struct.pack(">Q", usage_counter) + struct.pack(">Q", wallclock_nonce) + fp_h
    key = _hmac(sk1, b"shard")
    nonce = os.urandom(12)
    ct = ChaCha20Poly1305(key).encrypt(nonce, header + shard_key, None)
    return nonce + ct


def load_shard(sk1_handle: int, encrypted: bytes) -> DecryptedShard:
    sk1 = get_sk_from_handle(sk1_handle)
    key = _hmac(sk1, b"shard")
    nonce, ct = encrypted[:12], encrypted[12:]
    pt = ChaCha20Poly1305(key).decrypt(nonce, ct, None)
    shard_id = uuid.UUID(bytes=pt[:16])
    usage_counter = struct.unpack(">Q", pt[16:24])[0]
    wallclock_nonce = struct.unpack(">Q", pt[24:32])[0]
    fp_h = pt[32:64]
    if fp_h != _hmac(sk1, shard_id.bytes + get_device_fp()):
        raise ValueError("FP mismatch")
    shard_key = pt[64:]
    return DecryptedShard(shard_key, shard_id, usage_counter, wallclock_nonce)


def self_destruct_shard() -> None:
    pass
