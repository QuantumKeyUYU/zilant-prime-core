from __future__ import annotations

import hashlib
import time
from pathlib import Path

__all__ = ["generate_daily_challenge"]


def _db_path() -> Path:
    return Path.home() / ".zilant" / "challenge_db"


def generate_daily_challenge() -> str:
    day = time.strftime("%Y-%m-%d")
    challenge = hashlib.sha256(day.encode()).hexdigest()
    path = _db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(challenge)
    return challenge
