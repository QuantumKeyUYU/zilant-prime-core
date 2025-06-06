# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

from pathlib import Path

import pytest

from zilant_prime_core.utils.counter import (
    BACKUP_COUNTER_FILE,
    COUNTER_FILE,
    increment_counter,
    read_counter,
    write_counter,
)


@pytest.fixture(autouse=True)
def clean_counter_files(tmp_path: Path, monkeypatch):
    monkeypatch.setattr("zilant_prime_core.utils.counter.COUNTER_FILE", tmp_path / "cnt.txt")
    monkeypatch.setattr("zilant_prime_core.utils.counter.BACKUP_COUNTER_FILE", tmp_path / "cnt.bkp")
    # update imported constants
    globals()["COUNTER_FILE"] = tmp_path / "cnt.txt"
    globals()["BACKUP_COUNTER_FILE"] = tmp_path / "cnt.bkp"
    yield


def test_write_and_read_counter_basic():
    assert read_counter() == 0
    write_counter(5)
    assert read_counter() == 5
    assert COUNTER_FILE.exists()
    assert BACKUP_COUNTER_FILE.exists()
    assert read_counter() == 5


def test_increment_counter():
    write_counter(10)
    increment_counter()
    assert read_counter() == 11


def test_write_counter_invalid_value():
    with pytest.raises(ValueError):
        write_counter(-1)
    with pytest.raises(ValueError):
        write_counter("bad")  # type: ignore


def test_read_counter_backup_if_main_corrupt():
    BACKUP_COUNTER_FILE.write_text("42")
    COUNTER_FILE.write_text("not_int")
    assert read_counter() == 42
