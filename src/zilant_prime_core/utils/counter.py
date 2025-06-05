# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
"""Simple monotonic counter."""

from __future__ import annotations

import os
from pathlib import Path


class Counter:
    """Simple persistent monotonic counter."""

    def __init__(self, path: Path | None = None) -> None:
        self._path = path
        if path is not None and path.exists():
            try:
                self.value = int(path.read_text())
            except Exception:
                self.value = 0
        else:
            self.value = 0

    def increment(self) -> int:
        self.value += 1
        if self._path is not None:
            try:
                self._path.write_text(str(self.value))
            except Exception:
                pass
        return self.value
