__all__ = [
    'get_logger',
]

# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

import logging


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        logger.addHandler(handler)
    # Не понижаем ниже NOTSET (0), но INFO (20) уже удовлетворяет тесту level ≤ INFO
    logger.setLevel(logging.INFO)
    return logger
