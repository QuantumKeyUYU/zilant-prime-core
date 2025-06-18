from __future__ import annotations

import hashlib
import json
import time
from typing import Any


def record_action(action: str, params: dict[str, Any]) -> None:
    """Append an action entry to ``audit-ledger.jsonl``."""
    entry = {
        "timestamp": int(time.time()),
        "action": action,
        "params": params,
    }
    ser = json.dumps(entry, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(ser.encode()).hexdigest()
    entry["sha256"] = digest
    with open("audit-ledger.jsonl", "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")
