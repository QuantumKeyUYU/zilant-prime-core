# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

import logging

from zilant_prime_core.utils.logging import get_file_logger, get_logger


def test_get_logger_creates_and_reuses():
    log1 = get_logger("test")
    log2 = get_logger("test")
    assert log1 is log2
    assert isinstance(log1, logging.Logger)


def test_get_file_logger_writes(tmp_path, capsys):
    f = tmp_path / "out.log"
    logger = get_file_logger(str(f))
    # Уровень INFO по умолчанию
    logger.info("hello")
    logger.handlers[0].flush()
    text = f.read_text()
    assert "hello" in text

    # Повторный вызов возвращает тот же объект
    logger2 = get_file_logger(str(f))
    assert logger is logger2
