# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
"""Secret sharding utilities."""

from __future__ import annotations

from typing import List


def split_secret(secret: bytes, *, parts: int = 1) -> List[bytes]:
    """Split secret into ``parts`` shards (placeholder)."""
    return [secret]


def recover_secret(shards: List[bytes]) -> bytes:
    """Recover secret from shards (placeholder)."""
    return shards[0] if shards else b""
