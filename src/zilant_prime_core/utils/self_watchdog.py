# src/zilant_prime_core/utils/self_watchdog.py
# SPDX-FileCopyrightText: 2024–2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

from __future__ import annotations

import hashlib
import os
import sys
import threading
import time

from filelock import FileLock

__all__ = ["compute_self_hash", "init_self_watchdog"]


def compute_self_hash(file_path: str) -> str:
    """Вычислить SHA256-хеш указанного файла."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _watchdog_loop(file_path: str, expected_hash: str, interval: float) -> None:
    """Постоянно проверяет хеш и аварийно завершает процесс при несоответствии."""
    while True:
        current = compute_self_hash(file_path)
        if current != expected_hash:
            print(f"[watchdog] Self-hash mismatch on {file_path}! Exiting.", file=sys.stderr)
            os._exit(134)
        time.sleep(interval)


def init_self_watchdog(
    module_file: str | None = None,
    lock_file: str | None = None,
    interval: float = 60.0,
) -> None:
    """
    Инициализировать self-hash + watchdog:
      1. Захватывает файловую блокировку (FileLock) на lock_file.
      2. Вычисляет «эталонный» хеш модуля.
      3. Запускает daemon-поток, проверяющий хеш каждые `interval` секунд.
    """
    if module_file is None:
        module_file = os.path.realpath(__file__)
    if lock_file is None:
        lock_file = module_file + ".lock"

    lock = FileLock(lock_file)
    lock.acquire()  # держим блокировку до завершения процесса

    expected = compute_self_hash(module_file)
    t = threading.Thread(
        target=_watchdog_loop,
        args=(module_file, expected, interval),
        daemon=True,
    )
    t.start()
