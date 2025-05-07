import hashlib
from typing import Tuple

def vdf(data: bytes, iterations: int) -> bytes:
    """
    Очень простая VDF-функция для тестов:
    повторно хеширует SHA-256 входные данные заданное число итераций.
    """
    h = data
    for _ in range(iterations):
        h = hashlib.sha256(h).digest()
    return h

def compute_vdf(tries: int, iterations: int) -> bytes:
    """
    Генерирует VDF-доказательство для ZIL:
    1) Представляем `tries` в big-endian виде (хотя бы 1 байт).
    2) Повторно хешируем SHA-256 `iterations` раз.
    Возвращаем 32-байтный proof.
    """
    # определяем, сколько байт нужно для хранения tries:
    length = (tries.bit_length() + 7) // 8 or 1
    h = tries.to_bytes(length, 'big')
    for _ in range(iterations):
        h = hashlib.sha256(h).digest()
    return h

def verify_vdf(proof: bytes, tries: int, iterations: int) -> bool:
    """
    Проверяет валидность VDF-доказательства:
    просто сравниваем с вновь сгенерированным compute_vdf.
    """
    return proof == compute_vdf(tries, iterations)
