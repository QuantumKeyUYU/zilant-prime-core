# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
"""Generate decoy container files with random data."""

from __future__ import annotations

import os
import secrets
from pathlib import Path
from typing import Dict, List

from container import pack_file
from audit_ledger import record_decoy_purged, record_decoy_removed_early
import threading
import time

__all__ = ["generate_decoy_files", "sweep_expired_decoys"]

# track decoys and their expiration times
_DECOY_EXPIRY: Dict[Path, float] = {}


def generate_decoy_files(
    directory: Path,
    count: int,
    size: int = 1024,
    *,
    expire_seconds: int | None = None,
) -> List[Path]:
    """Create ``count`` decoy container files inside ``directory``.

    Parameters
    ----------
    directory: Path
        Directory to place decoy files.
    count: int
        How many decoy files to create.
    size: int
        Size of each file in bytes.
    """
    paths: List[Path] = []
    directory.mkdir(parents=True, exist_ok=True)
    for _ in range(max(0, count)):
        payload = os.urandom(size)
        tmp = directory / f"tmp_{secrets.token_hex(4)}"
        tmp.write_bytes(payload)
        out = directory / f"decoy_{secrets.token_hex(4)}.zil"
        pack_file(tmp, out, secrets.token_bytes(32))
        tmp.unlink()
        paths.append(out)
        if expire_seconds:
            _DECOY_EXPIRY[out] = time.time() + expire_seconds

    if expire_seconds:
        def _cleanup() -> None:
            time.sleep(expire_seconds)
            for p in paths:
                exp = _DECOY_EXPIRY.pop(p, None)
                if p.exists():
                    try:
                        p.unlink()
                        record_decoy_purged(str(p))
                    except FileNotFoundError:
                        record_decoy_removed_early(str(p))
                else:
                    record_decoy_removed_early(str(p))

        threading.Thread(target=_cleanup, daemon=True).start()

    return paths


def sweep_expired_decoys(directory: Path) -> int:
    """Remove expired decoy files in ``directory`` and log actions."""
    removed = 0
    now = time.time()
    for p in list(directory.glob("decoy_*.zil")):
        exp = _DECOY_EXPIRY.get(p)
        if exp is not None and now >= exp:
            try:
                p.unlink()
                record_decoy_purged(str(p))
            except FileNotFoundError:
                record_decoy_removed_early(str(p))
            _DECOY_EXPIRY.pop(p, None)
            removed += 1
    return removed
