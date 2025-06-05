import hashlib
import hmac
import os
import platform
import uuid
from typing import Dict

SALT_FP = bytes.fromhex("0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef")


def _collect_factors() -> Dict[str, str]:
    return {
        "cpu": platform.processor() or "unknown",
        "machine": platform.machine() or "unknown",
        "node": platform.node() or "unknown",
        "system": platform.system() or "unknown",
        "release": platform.release() or "unknown",
        "mac": hex(uuid.getnode()),
        "pid_count": str(len(os.listdir("/proc")) if os.path.exists("/proc") else 0),
        "random": os.urandom(8).hex(),
        "user": os.getenv("USER", "nobody"),
        "home": os.path.expanduser("~"),
    }


def get_device_fp() -> bytes:
    """Return concatenated HMACs of hardware factors."""
    factors = _collect_factors()
    out = []
    for name in sorted(factors.keys()):
        val = factors[name].encode()
        out.append(hmac.new(SALT_FP, val, hashlib.sha256).digest())
    return b"".join(out)
