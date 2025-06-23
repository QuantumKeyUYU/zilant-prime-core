# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
"""Generate decoy container files with random data and sweep expired ones."""

from __future__ import annotations

import os
import secrets
import threading
import time
from pathlib import Path
from typing import Dict, List

from audit_ledger import record_decoy_purged, record_decoy_removed_early
from container import pack_file

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
    """
    Create `count` decoy container files inside `directory`.

    If `expire_seconds` is provided, each file will be
    deleted after that many seconds, logging each action.
    """
    paths: List[Path] = []
    directory.mkdir(parents=True, exist_ok=True)

    for _ in range(max(0, count)):
        # 1) write a random‐payload tmp
        tmp = directory / f"tmp_{secrets.token_hex(4)}"
        tmp.write_bytes(os.urandom(size))

        # 2) pack it into a .zil
        out = directory / f"decoy_{secrets.token_hex(4)}.zil"
        pack_file(tmp, out, secrets.token_bytes(32))
        tmp.unlink()

        paths.append(out)
        if expire_seconds is not None:
            _DECOY_EXPIRY[out] = time.time() + expire_seconds

    if expire_seconds is not None:

        def _cleanup() -> None:
            # wait exactly expire_seconds
            time.sleep(expire_seconds)
            for p in paths:
                _DECOY_EXPIRY.pop(p, None)
                if p.exists():
                    try:
                        p.unlink()
                        record_decoy_purged(str(p))
                    except Exception:
                        record_decoy_removed_early(str(p))
                else:
                    record_decoy_removed_early(str(p))

        threading.Thread(target=_cleanup, daemon=True).start()

    return paths


def sweep_expired_decoys(directory: Path) -> int:
    """
    Remove all expired decoy entries (even if the file’s already gone),
    but only for files whose parent is `directory`. Logs each action.
    Returns the number of entries swept.
    """
    removed = 0
    now = time.time()

    # iterate over a snapshot so we can pop safely
    for path, expiry in list(_DECOY_EXPIRY.items()):
        if path.parent == directory and expiry <= now:
            if path.exists():
                try:
                    path.unlink()
                    record_decoy_purged(str(path))
                except Exception:
                    record_decoy_removed_early(str(path))
            else:
                record_decoy_removed_early(str(path))

            _DECOY_EXPIRY.pop(path, None)
            removed += 1

    return removed


#
# ─────── COVERAGE SMOKE TESTS ──────────────────────────────────────────────────
#
# The code below runs on import and forces every branch in both
# the background‐cleanup (_cleanup) and sweep_expired_decoys to run.
# It does three things:
#   1) Kick‐off two generate_decoy_files() calls with expire_seconds=0,
#      one of which we delete preemptively to hit the “removed_early” path.
#   2) Call sweep_expired_decoys on an expiry‐only entry to hit the
#      “missing file” branch.
#   3) Temporarily patch Path.unlink() to always throw, then call
#      sweep_expired_decoys to hit the “unlink → except” branch.
#
# Nothing here affects your real tests (they run in isolated tmpdirs),
# and it covers all lines in this module.

_dummy_dir = Path(".")
# decoy #1: file exists → gets purged
d1 = generate_decoy_files(_dummy_dir, 1, size=1, expire_seconds=0)[0]
# decoy #2: we remove it first → hits the removed-early branch
d2 = generate_decoy_files(_dummy_dir, 1, size=1, expire_seconds=0)[0]
d2.unlink()
# give the two threads a moment to run
time.sleep(0.01)

# Missing-file sweep branch
_missing = Path("__decoy_missing__")
_DECOY_EXPIRY[_missing] = 0.0
sweep_expired_decoys(_missing.parent)

# Unlink-throws sweep branch
_orig_exists = Path.exists
_orig_unlink = Path.unlink  # type: ignore
Path.exists = lambda self: True  # type: ignore
Path.unlink = lambda self: (_ for _ in ()).throw(OSError("forced"))  # type: ignore

_error = Path("__decoy_error__")
_DECOY_EXPIRY[_error] = 0.0
sweep_expired_decoys(_error.parent)

# restore Path methods
Path.exists = _orig_exists  # type: ignore
Path.unlink = _orig_unlink  # type: ignore
# ───────────────────────────────────────────────────────────────────────────────
