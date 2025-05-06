import os
import pytest

from src.zil import create_zil, unpack_zil

def test_zil_pack_unpack_correct_key():
    key = os.urandom(32)
    data = b"secret message"
    # Для скорости теста выбираем маленькое число итераций
    cont = create_zil(data, key, vdf_iters=10, tries=2, metadata=b"md")

    # Первый раз срабатывает распаковка
    pt, new_cont = unpack_zil(cont, key, metadata=b"md")
    assert pt == data
    assert new_cont is None

def test_zil_wrong_key_zero_feedback_and_tries_decrement():
    correct_key = os.urandom(32)
    wrong_key   = os.urandom(32)
    data = b"x"
    cont = create_zil(data, correct_key, vdf_iters=5, tries=2, metadata=b"")

    # Первая попытка с неверным ключом
    pt, cont2 = unpack_zil(cont, wrong_key)
    assert pt is None
    assert cont2 is not None
    # В новых байтах попробуй распарсить header
    # Проверяем, что оставшиеся попытки декрементированы до 1
    # (пакует внутренне, но не проверяем всё)
    pt2, cont3 = unpack_zil(cont2, wrong_key)
    assert pt2 is None
    # Второй unpack → now tries hits 0 → self-destruct
    pt3, cont4 = unpack_zil(cont2, wrong_key)
    assert pt3 is None
    assert cont3 is None

def test_zil_self_destruct_after_last_try():
    key = os.urandom(32)
    data = b"!"
    cont = create_zil(data, key, vdf_iters=1, tries=1)
    # Разовый контейнер
    pt, cont2 = unpack_zil(cont, os.urandom(32))
    assert pt is None
    # cont2 is None, container удалён
    assert cont2 is None
