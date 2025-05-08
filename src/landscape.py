# src/landscape.py (реальная реализация из коммита d294cfa)
"""
Генератор жёстких 3-SAT инстансов и анализ фазовых переходов (Σ_λ).
"""

from __future__ import annotations
import random
from typing import List, Tuple

class Formula:
    """
    Класс-обёртка для SAT-формулы.
    """
    def __init__(self, clauses: List[Tuple[int, int, int]]):
        self.clauses = clauses


def generate_sat(n: int) -> List[Tuple[int, int, int]]:
    """
    Генерирует n клауз для 3-SAT: каждая клауза — кортеж из 3 ненулевых литералов ±[1..n].
    """
    clauses: List[Tuple[int, int, int]] = []
    for _ in range(n):
        lits = set()
        while len(lits) < 3:
            v = random.randint(1, n)
            if random.choice((True, False)):
                v = -v
            lits.add(v)
        clauses.append(tuple(lits))
    return clauses


def compress(f: List[Tuple[int, int, int]], lam: float) -> Formula:
    """
    Преобразует список клауз в Formula (stub: просто обёртывает).
    """
    return Formula(f)


def energy(formula: Formula, lamb: float) -> float:
    """
    Энергетический функционал Σ_λ: unsat(formula) + λ * |formula|.
    """
    clauses = formula.clauses
    m = len(clauses)
    unsat = sum(1 for clause in clauses if not any(lit > 0 for lit in clause))
    return unsat + lamb * m


def find_phase_transition(
    n: int,
    lam: float,
    steps: int
) -> List[Tuple[int, float]]:
    """
    Сканирует плотность ребер от 1 до steps, возвращает список (density, energy).
    """
    results: List[Tuple[int, float]] = []
    for density in range(1, steps + 1):
        f = generate_sat(n)
        e = energy(Formula(f), lam)
        results.append((density, e))
    return results