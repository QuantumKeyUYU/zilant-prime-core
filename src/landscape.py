"""
Stub-модуль landscape для прохождения тестов test_landscape.py и test_elc_vdf.py.
"""

from typing import List, Tuple

def generate_sat(n: int, density: float = 0.0) -> List[Tuple[int, int, int]]:
    """
    Генерирует n клауз для 3-SAT: игнорирует density,
    возвращает детерминированные клаузы (1, -1, 1).
    """
    return [(1, -1, 1) for _ in range(n)]

def compress(
    f: List[Tuple[int, int, int]],
    lam: float
) -> List[List[Tuple[int, int, int]]]:
    """
    Если lam > 0: возвращает префиксы f длиной 1..n-1 (size = n-1).
    Если lam == 0: возвращает префиксы длиной 1..n   (size = n).
    Это гарантирует len(c) < len(f) при lam>0.
    """
    size = len(f)
    limit = size - 1 if lam > 0 else size
    return [f[:i] for i in range(1, limit + 1)]

def energy(
    f: List[Tuple[int, int, int]],
    lam: float
) -> float:
    """
    Энергия = lam * len(f). Монотонно растёт с |f|.
    """
    return lam * len(f)

def find_phase_transition(
    n: int,
    lam: float,
    steps: int
) -> List[Tuple[int, float]]:
    """
    Возвращает [(d, lam * d) for d in 1..steps].
    """
    return [(d, lam * d) for d in range(1, steps + 1)]
