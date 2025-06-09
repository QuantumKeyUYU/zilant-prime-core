# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

import os
import random
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
    check_dir = Path(tmp_dir) if tmp_dir else Path(os.getenv("TMP", "/tmp"))
    for f in check_dir.iterdir():
        if not f.is_file():
            continue
        if is_honeyfile(str(f)):
            raise HoneyfileError(f"Honeyfile detected: {f}")
