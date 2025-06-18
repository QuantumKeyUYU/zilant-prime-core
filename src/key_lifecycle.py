"""Key lifecycle utilities and audit log."""

from __future__ import annotations

import hashlib
import secrets
from pathlib import Path
from typing import List

import shamir


class KeyLifecycle:
    """Key derivation and rotation helpers."""

    @staticmethod
    def derive_session_key(master_key: bytes, context: str) -> bytes:
        """Derive a session key.

        Args:
            master_key: Master key bytes.
            context: Usage context string.

        Returns:
            Derived session key bytes.
        """
        h = hashlib.blake2s(context.encode("utf-8"), key=master_key)
        return h.digest()

    @staticmethod
    def rotate_master_key(old_key: bytes, days: int) -> bytes:
        """Rotate ``old_key`` using ``days`` as salt.

        Args:
            old_key: Current master key.
            days: Rotation interval in days.

        Returns:
            New master key bytes.
        """
        data = days.to_bytes(4, "big", signed=False)
        return hashlib.blake2s(data, key=old_key).digest()


def shard_secret(secret: bytes, n: int, t: int) -> List[bytes]:
    """Split ``secret`` into ``n`` shares with threshold ``t``.

    Args:
        secret: Secret bytes to split. Must fit into 127 bits.
        n: Total number of shares.
        t: Minimum shares required to recover.

    Returns:
        List of share blobs.
    """
    if not 1 <= t <= n:
        raise ValueError("invalid threshold")
    value = int.from_bytes(secret, "big")
    if value >= shamir._PRIME:
        raise ValueError("secret too large")
    poly = [value] + [secrets.randbelow(shamir._PRIME) for _ in range(t - 1)]

    def eval_at(x: int) -> int:
        accum = 0
        for coeff in reversed(poly):
            accum = (accum * x + coeff) % shamir._PRIME
        return accum

    shares = [i.to_bytes(1, "big") + eval_at(i).to_bytes(16, "big") for i in range(1, n + 1)]
    return shares


def recover_secret(shards: List[bytes]) -> bytes:
    """Recover a secret from ``shards`` produced by :func:`shard_secret`.

    Args:
        shards: Share blobs.

    Returns:
        Reconstructed secret bytes.
    """
    if len(shards) < 1:
        return b""
    points = []
    for sh in shards:
        if len(sh) < 17:
            raise ValueError("invalid shard")
        x = sh[0]
        y = int.from_bytes(sh[1:17], "big")
        points.append((x, y))
    secret_int = shamir.recover_secret(points)
    length = (secret_int.bit_length() + 7) // 8
    return secret_int.to_bytes(length, "big")


class AuditLog:
    """Append-only audit log secured by hash chaining."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or Path("audit.log")

    def append_event(self, event: str) -> None:
        """Append ``event`` to the log."""
        prev = self._last_digest()
        digest = hashlib.sha256(prev + event.encode("utf-8")).digest()
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(f"{digest.hex()} {event}\n")

    def _last_digest(self) -> bytes:
        if not self.path.exists():
            return b""
        *_, last = self.path.read_bytes().splitlines()
        hex_digest = last.split(b" ", 1)[0]
        return bytes.fromhex(hex_digest.decode())

    def verify_log(self) -> bool:
        """Verify integrity of the log."""
        digest = b""
        if not self.path.exists():
            return True
        for line in self.path.read_text(encoding="utf-8").splitlines():
            hex_digest, event = line.split(" ", 1)
            digest = hashlib.sha256(digest + event.encode("utf-8")).digest()
            if digest.hex() != hex_digest:
                return False
        return True
