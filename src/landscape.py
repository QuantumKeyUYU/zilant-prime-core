"""
Мини-генератор элементарных SAT-«пейзажей» и быстрая проверка решения.

* `generate_sat(nvars, nclauses, lits_per_clause=3)` → CNF-список.
* `verify_sat(cnf, assignment)` возвращает `True/False` или
  поднимает `ValueError`, если переменных в назначении не хватает.
"""

from __future__ import annotations

import random
from typing import List, Sequence

Literal = int
Clause = List[Literal]
CNF = List[Clause]

__all__ = ["generate_sat", "verify_sat", "CNF"]


def _rand_literal(nvars: int) -> Literal:
    var = random.randint(1, nvars)
    return var if random.choice((True, False)) else -var


def generate_sat(nvars: int, nclauses: int, lits_per_clause: int = 3) -> CNF:
    """Сгенерировать псевдо-случайную CNF‐формулу (k-SAT)."""
    return [[_rand_literal(nvars) for _ in range(lits_per_clause)] for _ in range(nclauses)]


def verify_sat(cnf: CNF, assignment: Sequence[bool]) -> bool:
    """
    Проверить, удовлетворяет ли булевое `assignment` формуле `cnf`.

    * `assignment[i]` — значение переменной *i+1*.
    * Положительный литерал `k` истинен, если `assignment[k-1] is True`.
    * Отрицательный `-k` истинен, если `assignment[k-1] is False`.
    """
    if any(abs(lit) > len(assignment) for clause in cnf for lit in clause):
        raise ValueError("assignment shorter than variable id in CNF")

    for clause in cnf:
        if not any((assignment[abs(lit) - 1]) ^ (lit < 0) for lit in clause):
            return False
    return True
