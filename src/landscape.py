# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

"""Мини-«пейзаж» из (clauses, salts) с добровольной strict-валидацией."""

from __future__ import annotations
import random
from typing import Any, List, Tuple


def generate_landscape(size: int, *, strict: bool = False) -> Tuple[List[int], List[int]]:
    """
    Генерирует «пейзаж» длины size:
      - clauses — случайные числа 0–255 (или 0–1, если strict=True)
      - salts   — случайные int для солей

    :raises ValueError: если size <= 0
    """
    if size <= 0:
        raise ValueError("size must be positive")

    clauses: List[int] = []
    salts:   List[int] = []

    for _ in range(size):
        # если строгий режим — только 0 или 1, иначе полное 0–255
        clause = random.randint(0, 1) if strict else random.randint(0, 255)
        clauses.append(clause)
        salts.append(random.randint(0, 2**31 - 1))

    return clauses, salts


def verify_landscape(obj: Any, *, strict: bool = False) -> bool:
    """
    Верифицирует объект как (clauses, salts):
      - clauses и salts должны быть списками одинаковой длины
      - если strict=True, clauses допускаются только 0 или 1
      - в любом случае все элементы должны быть int

    :raises ValueError: если структура obj не соответствует tuple[list,int] или длины разные
    """
    if not (isinstance(obj, tuple) and len(obj) == 2 and
            all(isinstance(lst, list) for lst in obj)):
        raise ValueError("Landscape must be tuple(list[int], list[int])")

    clauses, salts = obj
    if len(clauses) != len(salts):
        raise ValueError("Clauses and salts must have same length")

    # Явно указываем strict=False, чтобы ruff не ругался B905
    for clause, salt in zip(clauses, salts, strict=False):
        if not isinstance(clause, int) or not isinstance(salt, int):
            return False
        if strict and clause not in (0, 1):
            return False

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
