# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

"""Anti-snapshot lock and checks."""

from __future__ import annotations

import hashlib
import hmac
import os
import struct
import time
from pathlib import Path

from .crypto_wrapper import get_sk_bytes
from .logging import self_destruct_all

LOCK_PATH = "/var/lock/pseudohsm.lock"


def acquire_snapshot_lock(sk1_handle: int) -> None:
    data = struct.pack(">IQ", os.getpid(), int(time.time())) + os.urandom(8)
    mac = hmac.new(get_sk_bytes(sk1_handle), data, hashlib.sha256).digest()
    Path(LOCK_PATH).write_bytes(data + mac)


def check_snapshot_freshness(sk1_handle: int) -> None:
    path = Path(LOCK_PATH)
    if not path.exists():
        return
    blob = path.read_bytes()
    if len(blob) != 20 + 32:
        self_destruct_all()
    data = blob[:20]
    mac = blob[20:52]
    expected = hmac.new(get_sk_bytes(sk1_handle), data, hashlib.sha256).digest()
    if not hmac.compare_digest(mac, expected):
        self_destruct_all()
    pid, timestamp = struct.unpack(">IQ", data[:12])
    if time.time() - timestamp > 300:
        self_destruct_all()
    try:
        os.kill(pid, 0)
    except OSError:
        self_destruct_all()
