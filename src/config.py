from __future__ import annotations

"""Project configuration options."""

from pathlib import Path

import tomllib

ROOT = Path(__file__).resolve().parents[1]


def _load_pq_mode() -> str:
    try:
        data = tomllib.loads((ROOT / "pyproject.toml").read_text())
        return data.get("tool", {}).get("zilant", {}).get("pq_mode", "classic")
    except Exception:
        return "classic"


PQ_MODE: str = _load_pq_mode()
