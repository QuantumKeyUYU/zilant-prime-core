# src/zilant_prime_core/utils/self_watchdog.py
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

from __future__ import annotations

import hashlib
import os
import sys
import threading
import time

from filelock import FileLock

__all__ = ["compute_self_hash", "init_self_watchdog", "cross_watchdog"]


def compute_self_hash(file_path: str) -> str:
    """Вычислить SHA256-хеш указанного файла."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _watchdog_loop(file_path: str, expected_hash: str, interval: float) -> None:
    """
    Постоянно проверяет хеш и аварийно завершает процесс при несоответствии
    или при любой ошибке при чтении/хешировании.
    """
    while True:
        try:
            current = compute_self_hash(file_path)
        except Exception:
            # Если не удалось прочитать/просчитать хеш — немедленно выходим
            os._exit(134)
        if current != expected_hash:
            print(f"[watchdog] Self-hash mismatch on {file_path}! Exiting.", file=sys.stderr)
            os._exit(134)
        time.sleep(interval)


def cross_watchdog(interval: float = 1.0) -> None:
    parent_pid = os.getppid()
    while True:
        try:
            os.kill(parent_pid, 0)
        except OSError:
            sys.exit(1)
        time.sleep(interval)


def init_self_watchdog(
    module_file: str | None = None,
    lock_file: str | None = None,
    interval: float = 60.0,
) -> None:
    """
    Инициализировать self‐watchdog:
      1. Захватывает файловую блокировку (FileLock) на lock_file.
      2. Вычисляет «эталонный» хеш модуля.
      3. Запускает daemon‐поток, проверяющий хеш каждые `interval` секунд.
    """
    if module_file is None:
        module_file = os.path.realpath(__file__)
    if lock_file is None:
        lock_file = module_file + ".lock"

    parent_pid = os.getppid()
    try:
        os.kill(parent_pid, 0)
    except OSError:
        sys.exit(1)

    # Шаг 1: блокировка
    lock = FileLock(lock_file)
    lock.acquire()

    # Шаг 2: вычисляем «эталонный» хеш
    expected_hash = compute_self_hash(module_file)

    # Шаг 3: создаем поток‐«часовой механизм»
    t1 = threading.Thread(
        target=_watchdog_loop,
        args=(module_file, expected_hash, interval),
        daemon=True,
    )
    if not hasattr(t1, "start"):
        raise RuntimeError("Thread object missing 'start' method")
    t1.start()
    first_args = getattr(threading.Thread, "args", None)

    t2 = threading.Thread(target=cross_watchdog, args=(interval / 2,), daemon=True)
    if hasattr(threading.Thread, "args"):
        threading.Thread.args = first_args
    t2.start()
