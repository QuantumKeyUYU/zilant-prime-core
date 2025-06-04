import json
import os
from datetime import datetime

__all__ = ["log_suspicious_event"]

SUSPICION_LOG = os.environ.get("ZILANT_SUSPICION_LOG", "suspicion.log")


def log_suspicious_event(event: str, details: dict[str, object]) -> None:
    """Append suspicious event as JSON line."""
    entry = {"time": datetime.utcnow().isoformat() + "Z", "event": event}
    entry.update(details)  # type: ignore[arg-type]
    os.makedirs(os.path.dirname(SUSPICION_LOG) or ".", exist_ok=True)
    with open(SUSPICION_LOG, "a") as f:
        f.write(json.dumps(entry, separators=(",", ":")) + "\n")


# Backwards compatibility


def increment_suspicion(reason: str) -> None:  # pragma: no cover - legacy
    log_suspicious_event(reason, {})
