# ── файл src/landscape.py ─────────────────────────────────────────────────────

from typing import Sequence, Tuple

def energy(data: Sequence[Tuple[int, int]]) -> int:
    """
    Пример: ваша реализация подсчёта "энергии" ландшафта.
    Принимает список (или другой итерабельный контейнер) кортежей (x,y)
    и возвращает число.
    """
    # <-- Ваша реальная логика должна стоять здесь! -->
    total = 0
    for x, y in data:
        total += x*x + y*y
    return total

def generate_sat(data: Sequence[Tuple[int, int]]) -> int:
    """
    Тесты из tests/test_elc_vdf.py ожидают функцию generate_sat,
    возвращающую то же, что energy.
    """
    return energy(data)
