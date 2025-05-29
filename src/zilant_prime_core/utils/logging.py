# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging
from pathlib import Path

__all__ = ["get_logger", "get_file_logger"]


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Возвращает консольный логгер с уровнем INFO.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger


def get_file_logger(log_path: str) -> logging.Logger:
    """
    Возвращает файловый логгер с уровнем INFO, записывающий в файл `log_path`.
    Если файл ещё не существует, создаёт его.
    """
    # гарантируем, что сам файл существует, чтобы .read_text() не падал до первого сообщения
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)
    Path(log_path).touch(exist_ok=True)

    logger = logging.getLogger(f"file:{log_path}")
    if not logger.handlers:
        handler = logging.FileHandler(log_path, encoding="utf-8")
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger
