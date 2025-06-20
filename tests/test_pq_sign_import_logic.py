# tests/test_pq_sign_import_logic.py

import importlib.util
import sys


def _load_pq_sign(fake_oqs_module):
    # Подменяем oqs в sys.modules, динамически загружаем код модуля
    sys.modules["oqs"] = fake_oqs_module
    spec = importlib.util.find_spec("zilant_prime_core.utils.pq_sign")
    mod = importlib.util.spec_from_file_location("tmp_pq_sign", spec.origin)
    tmp = importlib.util.module_from_spec(mod)
    mod.loader.exec_module(tmp)
    return tmp


def test_pq_sign_detects_no_signature():
    fake = type("Oqs", (), {})()  # нет атрибута Signature
    tmp = _load_pq_sign(fake)
    assert tmp._HAS_OQS is False


def test_pq_sign_detects_signature():
    class Fake:
        def Signature(self, alg):
            return None

    tmp = _load_pq_sign(Fake)
    assert tmp._HAS_OQS is True
