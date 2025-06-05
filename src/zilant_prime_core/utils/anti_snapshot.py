# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
"""Environment anti-snapshot detection placeholders."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

_LOCK_PATH = Path("/tmp/zilant_snapshot.lock")


def detect_snapshot(lock_path: Path | None = None, *, max_age: float = 300.0) -> bool:
    """Detect snapshot/rollback by checking a simple lock file."""
    path = lock_path or _LOCK_PATH
    now = time.time()
    data = {"pid": os.getpid(), "ts": now}

    if path.exists():
        try:
            loaded = json.loads(path.read_text())
            pid = int(loaded.get("pid", 0))
            ts = float(loaded.get("ts", 0.0))
            # Existing lock: if PID dead or timestamp too old, assume snapshot
            if pid != os.getpid() and not os.path.exists(f"/proc/{pid}"):
                return True
            if now - ts > max_age:
                return True
        except Exception:
            return True

    try:
        path.write_text(json.dumps(data))
    except Exception:
        pass
    return False
