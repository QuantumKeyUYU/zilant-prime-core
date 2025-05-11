from typing import Sequence

def energy(state: Sequence[float]) -> float:
    """
    Вычисляет «энергию» состояния как сумму квадратов координат.
    state — любая последовательность чисел (int или float).
    Возвращает float.
    """
    return float(sum(x * x for x in state))
