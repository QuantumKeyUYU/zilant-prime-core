import logging
from zilant_prime_core.utils.logging import get_logger


def test_get_logger_creates_logger():
    name = "zilant_test"
    logger = get_logger(name)
    assert isinstance(logger, logging.Logger)
    # у него должен быть хотя бы один handler
    assert logger.handlers
    # уровень INFO или ниже
    assert logger.level <= logging.INFO
