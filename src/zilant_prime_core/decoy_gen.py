# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
"""
Генерация/уборка файлов-приманок («decoy»).

* TTL хранится в mtime самого .zil-файла — без побочных .json.
* Все функции thread-safe и кроссплатформенны.
"""

from __future__ import annotations

import os
import time
from hashlib import sha256
from pathlib import Path
from typing import List

__all__ = [
    "generate_decoy_file",
    "generate_decoy_files",
    "sweep_expired_decoys",
]


# ──────────────────────────── helpers ────────────────────────────
def _set_expiry(path: Path, expires_at: float) -> None:
    """Записываем TTL в atime/mtime."""
    os.utime(path, (expires_at, expires_at))


# ──────────────────────────── creators ───────────────────────────
def generate_decoy_file(
    dest: Path,
    size: int = 1024,
    expire_seconds: float = 60.0,
) -> Path:
    """
    Создать одиночный decoy-файл *dest*.

    Parameters
    ----------
    dest : Path
        Должен оканчиваться `.zil`.
    size : int
        Размер случайных данных.
    expire_seconds : float
        Через сколько секунд файл протухнет.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(os.urandom(max(1, size)))
    _set_expiry(dest, time.time() + expire_seconds)
    return dest


def generate_decoy_files(
    dest_dir: Path,
    count: int = 1,
    size: int = 1024,
    expire_seconds: float = 60.0,
) -> List[Path]:
    """Сгенерировать пачку приманок в *dest_dir* и вернуть их пути."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    created: List[Path] = []
    for _ in range(count):
        fname = dest_dir / f"decoy_{sha256(os.urandom(8)).hexdigest()[:8]}.zil"
        created.append(generate_decoy_file(fname, size, expire_seconds))
    return created


# ──────────────────────────── sweeper ────────────────────────────
def sweep_expired_decoys(dir_path: Path) -> int:
    """
    Удалить все `.zil`-файлы в *dir_path*, чей mtime ≤ текущего времени.

    Возвращает количество успешно удалённых файлов.

    *Почему не glob()*
    `Path.glob("*.zil")` иногда падает с `IsADirectoryError`, если во время
    обхода подкаталог внезапно исчез. Проходимся `iterdir()` и ловим гонки
    вручную — так надёжнее.
    """
    removed, now = 0, time.time()

    try:
        entries = dir_path.iterdir()
    except FileNotFoundError:
        # Каталог уже исчез к моменту вызова
        return 0

    for entry in entries:
        try:
            # берём только реальные файлы с нужным суффиксом
            if entry.suffix != ".zil" or not entry.is_file():
                continue

            if entry.stat().st_mtime <= now:
                entry.unlink(missing_ok=True)
                removed += 1

        except (FileNotFoundError, NotADirectoryError, IsADirectoryError):
            # Файл/папка пропали между iterdir() и stat()/unlink()
            continue

    return removed
