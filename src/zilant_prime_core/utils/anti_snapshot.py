# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

"""Anti-snapshot lock and checks."""

from __future__ import annotations

import hashlib
import hmac
import os
import struct
import tempfile
import time
from pathlib import Path

from .crypto_wrapper import get_sk_bytes
from .logging import self_destruct_all

if os.name == "nt":
    base = Path(os.getenv("LOCALAPPDATA", tempfile.gettempdir())) / "ZilantPrime"
else:
    base = Path("/var/lock")
    if not base.exists():
        base = Path(tempfile.gettempdir())
LOCK_PATH = str(base / "pseudohsm.lock")


def acquire_snapshot_lock(sk1_handle: int) -> None:
    data = struct.pack(">IQ", os.getpid(), int(time.time())) + os.urandom(8)
    mac = hmac.new(get_sk_bytes(sk1_handle), data, hashlib.sha256).digest()
    path = Path(LOCK_PATH)
    tmp = path.with_suffix(".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(tmp, "wb") as f:
            f.write(data + mac)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            tmp.unlink(missing_ok=True)
        except Exception:
            pass
        self_destruct_all()


def check_snapshot_freshness(sk1_handle: int) -> None:
    path = Path(LOCK_PATH)
    if not path.exists():
        return
    try:
        blob = path.read_bytes()
        if len(blob) != 20 + 32:
            raise ValueError
        data = blob[:20]
        mac = blob[20:52]
        expected = hmac.new(get_sk_bytes(sk1_handle), data, hashlib.sha256).digest()
        if not hmac.compare_digest(mac, expected):
            raise ValueError
        pid, timestamp = struct.unpack(">IQ", data[:12])
        if time.time() - timestamp > 300:
            raise ValueError
        os.kill(pid, 0)
    except Exception:
        self_destruct_all()
