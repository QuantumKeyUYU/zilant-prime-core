# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

__all__ = [
    "get_logger",
]

# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT
"""
Мини-обёртка над стандартным `logging`, чтобы избежать жёсткой зависимости
от конкретных конфигураций в CLI/тестах.
"""

from __future__ import annotations

import logging

_LOGGER_NAME = "zilant"


def setup_logging(verbose: bool = False) -> None:
    """Инициализировать root-логгер (idempotent)."""
    if logging.getLogger().handlers:  # уже настроен
        return

    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        format="%(levelname).1s │ %(message)s",
        level=level,
    )


def log(msg: str, *args, **kwargs) -> None:  # noqa: D401 (plain wrapper)
    """Сокращение: `logging.getLogger("zilant").info(...)`."""
    logging.getLogger(_LOGGER_NAME).info(msg, *args, **kwargs)
