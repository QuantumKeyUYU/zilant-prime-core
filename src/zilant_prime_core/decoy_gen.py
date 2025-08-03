# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
"""
Генерация/уборка файлов-приманок («decoy»).

* TTL хранится в `mtime` самого `.zil`-файла – никаких побочных `.json`.
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


def _set_expiry(path: Path, expires_at: float) -> None:
    """Меняем atime/mtime, сохраняя TTL внутри самого файла."""
    os.utime(path, (expires_at, expires_at))


def generate_decoy_file(
    dest: Path,
    size: int = 1024,
    expire_seconds: float = 60.0,
) -> Path:
    """
    Создать одиночный decoy-файл *dest*.

    Parameters
    ----------
    dest:
        Полный путь до создаваемого файла (должен оканчиваться `.zil`).
    size:
        Размер случайных данных (байт). Для тестов обычно 16–64 B.
    expire_seconds:
        Через сколько секунд файл считается «протухшим».
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
    """
    Сгенерировать пачку приманок в каталоге *dest_dir*.

    Возвращает список созданных путей (только `.zil`, без побочных файлов).
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    created: List[Path] = []
    for _ in range(count):
        fname = dest_dir / f"decoy_{sha256(os.urandom(8)).hexdigest()[:8]}.zil"
        created.append(generate_decoy_file(fname, size, expire_seconds))
    return created


def sweep_expired_decoys(dir_path: Path) -> int:
    """
    Удалить все decoy-файлы из *dir_path*, у которых `mtime` ≤ time.time().

    Возвращает количество успешно удалённых файлов.
    """
    removed = 0
    now = time.time()
    for path in dir_path.glob("*.zil"):
        try:
            # пропускаем всё, что не файл
            if not path.is_file():
                continue
            # если срок истёк — удаляем
            if path.stat().st_mtime <= now:
                path.unlink(missing_ok=True)
                removed += 1
        except (FileNotFoundError, NotADirectoryError, IsADirectoryError):
            # файл/папка уже пропали или путь оказался директорией — игнорируем
            continue
    return removed
