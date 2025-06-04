from __future__ import annotations

import os
import time

__all__ = ["increment_suspicion"]


def increment_suspicion(reason: str) -> None:
    path = os.path.expanduser("~/.zilant/suspicion.log")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a") as f:
        f.write(f"{int(time.time())}:{reason}\n")
