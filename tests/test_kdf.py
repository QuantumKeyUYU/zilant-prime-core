import pytest
from src.kdf import derive_key, DEFAULT_SALT_LENGTH

def test_default_derive_key():
    password = b"test_password"
    key = derive_key(password)
    assert len(key) == 32

def test_custom_salt():
    password = b"test_password"
    salt = b'a' * DEFAULT_SALT_LENGTH
    key1 = derive_key(password, salt=salt)
    key2 = derive_key(password, salt=salt)
    assert key1 == key2

def test_invalid_salt_length():
    password = b"test_password"
    invalid_salt = b'short_salt'
    with pytest.raises(ValueError):
        derive_key(password, salt=invalid_salt)

@pytest.mark.parametrize("time_cost", [1, 5, 10])
@pytest.mark.parametrize("mem_cost", [8192, 65536, 1048576])
@pytest.mark.parametrize("parallelism", [1, 4, 16])
def test_parameterized_derive_key(time_cost, mem_cost, parallelism):
    password = b"test_password"
    key = derive_key(password, time_cost=time_cost, mem_cost=mem_cost, parallelism=parallelism)
    assert len(key) == 32

@pytest.mark.parametrize("time_cost", [0, 11])
def test_invalid_time_cost(time_cost):
    password = b"test_password"
    with pytest.raises(ValueError):
        derive_key(password, time_cost=time_cost)

@pytest.mark.parametrize("mem_cost", [4096, 2097152])  # too small & too large
def test_invalid_mem_cost(mem_cost):
    password = b"test_password"
    with pytest.raises(ValueError):
        derive_key(password, mem_cost=mem_cost)

@pytest.mark.parametrize("parallelism", [0, 17])
def test_invalid_parallelism(parallelism):
    password = b"test_password"
    with pytest.raises(ValueError):
        derive_key(password, parallelism=parallelism)
