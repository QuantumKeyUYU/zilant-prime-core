from __future__ import annotations

"""Adaptive decoy data generator (offline LLM stub)."""

import random
from typing import Dict

__all__ = ["generate"]

_FAKE_NAMES = [
    "report.pdf",
    "invoice.pdf",
    "photo.jpg",
    "scan.jpg",
    "notes.txt",
    "draft.docx",
]


def generate(seed: int | None = None, schema: str | None = None) -> Dict[str, bytes]:
    """Return fake file map using *seed* for reproducibility."""
    rnd = random.Random(seed)
    count = rnd.randint(5, 8)
    paths: Dict[str, bytes] = {}
    for i in range(count):
        base = rnd.choice(_FAKE_NAMES)
        name = f"{rnd.randint(1000,9999)}_{base}"
        paths[name] = b"\0" * 4096
    return paths
