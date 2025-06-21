# src/zilant_prime_core/utils/honeyfile.py
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core Contributors

import os
import random
import tempfile
from pathlib import Path


class HoneyfileError(Exception):
    pass


def create_honeyfile(path: str) -> None:
    marker = f"HONEYFILE:{random.randint(1000, 9999)}"
    p = Path(path)
    content = p.read_text(encoding="utf-8") if p.exists() else ""
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"{content}\n{marker}")


def is_honeyfile(path: str) -> bool:
    try:
        content = Path(path).read_text(encoding="utf-8")
        return "HONEYFILE:" in content
    except Exception:
        return False


def check_tmp_for_honeyfiles(tmp_dir: str | None = None) -> None:
    """Scan temporary directory for honeyfiles in a secure, portable way."""
    if tmp_dir is not None:
        check_dir = Path(tmp_dir)
    else:
        # Respect TMPDIR/TMP/TEMP environment variables if set, else use default
        dir_env = os.environ.get("TMPDIR") or os.environ.get("TMP") or os.environ.get("TEMP")
        if dir_env:
            check_dir = Path(dir_env)
        else:
            check_dir = Path(tempfile.gettempdir())  # pragma: no cover
    for f in check_dir.iterdir():
        if not f.is_file():
            continue
        if is_honeyfile(str(f)):
            raise HoneyfileError(f"Honeyfile detected: {f}")
