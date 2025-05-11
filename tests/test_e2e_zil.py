# tests/test_e2e_zil.py

import pytest

from src.zil import (
    SelfDestructError,
    pack_zil_file,
    unpack_zil_file,
)

# Параметры для теста (замените на реальные)
FORMULA = ...  # ваш VDF-formula callable
LAMBDA = ...  # float
STEPS = ...  # int
KEY = b"\x00" * 32
SALT = b"\x01" * 16
NONCE = b"\x02" * 12


def test_one_time_file_removal(tmp_path):
    path = tmp_path / "one_time.zil"
    pack_zil_file(
        str(path),
        b"secret",
        FORMULA,
        LAMBDA,
        STEPS,
        KEY,
        SALT,
        NONCE,
        {"tries": 0},
        max_tries=3,
        one_time=True,
    )
    data = unpack_zil_file(str(path), FORMULA, KEY)
    assert data == b"secret"
    assert not path.exists()


def test_wrong_key_increments_tries_and_removes(tmp_path):
    path = tmp_path / "fail.zil"
    pack_zil_file(
        str(path),
        b"foo",
        FORMULA,
        LAMBDA,
        STEPS,
        KEY,
        SALT,
        NONCE,
        {"tries": 0},
        max_tries=2,
        one_time=False,
    )
    with pytest.raises(Exception):
        unpack_zil_file(str(path), FORMULA, b"wrong" * 6)
    assert path.exists()

    with pytest.raises(SelfDestructError):
        unpack_zil_file(str(path), FORMULA, b"wrong" * 6)
    assert not path.exists()


def test_multiple_opens(tmp_path):
    path = tmp_path / "multi.zil"
    pack_zil_file(
        str(path),
        b"data",
        FORMULA,
        LAMBDA,
        STEPS,
        KEY,
        SALT,
        NONCE,
        {"tries": 0},
        max_tries=3,
        one_time=False,
    )
    for i in range(3):
        out = unpack_zil_file(str(path), FORMULA, KEY)
        assert out == b"data"
        if i < 2:
            assert path.exists()
        else:
            assert not path.exists()
