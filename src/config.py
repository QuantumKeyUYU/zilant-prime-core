from __future__ import annotations

"""Project configuration options."""

import tomllib

from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _load_option(name: str, default: str) -> str:
    try:
        data = tomllib.loads((ROOT / "pyproject.toml").read_text())
        return str(data.get("tool", {}).get("zilant", {}).get(name, default))
    except Exception:
        return default


PQ_MODE: str = _load_option("pq_mode", "classic")
BACKEND_TYPE: str = _load_option("backend_type", "local")


def get_storage_backend() -> Any:
    """Return storage backend module according to ``backend_type``."""
    if BACKEND_TYPE == "s3":
        from backends import s3_backend

        return s3_backend
    if BACKEND_TYPE == "ipfs":
        from backends import ipfs_backend

        return ipfs_backend
    from backends import local_backend

    return local_backend
