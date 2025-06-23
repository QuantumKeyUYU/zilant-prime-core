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


def record_decoy_event(info: dict[str, Any]) -> None:
    """Shortcut to log a decoy-related event."""
    record_action("decoy_event", info)


def record_decoy_purged(path: str) -> None:
    """Log that a decoy file was purged automatically."""
    record_action("decoy_purged", {"file": path})


def record_decoy_removed_early(path: str) -> None:
    """Log that a decoy disappeared before its expiration."""
    record_action("decoy_removed_early", {"file": path})


def record_self_heal_triggered(info: dict[str, Any]) -> None:
    """Log that self-heal was triggered."""
    record_action("self_heal_triggered", info)


def record_self_heal_done(info: dict[str, Any]) -> None:
    """Log that self-heal completed successfully."""
    record_action("self_heal_done", info)
