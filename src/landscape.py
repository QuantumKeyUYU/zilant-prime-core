# ruff: noqa: F404,F811,B905,E741
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

"""
Мини-«пейзаж» из (clauses, salts) с добровольной strict-валидацией,
а также генератор и верификатор простых SAT‐формул.

Функции:
  - generate_landscape(size: int, *, strict: bool=False) → tuple[list[int], list[int]]
  - verify_landscape(obj: Any, *, strict: bool=False) → bool
  - generate_sat(nvars: int, nclauses: int, lits_per_clause: int=3) → list[list[int]]
  - verify_sat(cnf: list[list[int]], assignment: Sequence[bool]) → bool
"""

from __future__ import annotations

import random
from typing import Any, List, Sequence, Tuple

Literal = int
Clause = List[Literal]
CNF = List[Clause]

__all__ = ["generate_landscape", "verify_landscape", "generate_sat", "verify_sat", "CNF"]


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
    salts: List[int] = []

    for _ in range(size):
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

    :raises ValueError: если структура obj не соответствует tuple[list[int], list[int]]
                         или длины разные
    """
    if not (isinstance(obj, tuple) and len(obj) == 2 and all(isinstance(lst, list) for lst in obj)):
        raise ValueError("Landscape must be tuple(list[int], list[int])")

    clauses, salts = obj
    if len(clauses) != len(salts):
        raise ValueError("Clauses and salts must have same length")

    for clause, salt in zip(clauses, salts, strict=False):
        if not isinstance(clause, int) or not isinstance(salt, int):
            return False
        if strict and clause not in (0, 1):
            return False

    return True


def _rand_literal(nvars: int) -> Literal:
    var = random.randint(1, nvars)
    return var if random.choice((True, False)) else -var


def generate_sat(nvars: int, nclauses: int, lits_per_clause: int = 3) -> CNF:
    """
    Сгенерировать псевдо-случайную CNF-формулу (k-SAT).
    """
    return [[_rand_literal(nvars) for _ in range(lits_per_clause)] for _ in range(nclauses)]


def verify_sat(cnf: CNF, assignment: Sequence[bool]) -> bool:
    """
    Проверить, удовлетворяет ли булевое `assignment` формуле `cnf`.

    :raises ValueError: если в `cnf` встречается литерал с номером больше len(assignment)
    """
    if any(abs(lit) > len(assignment) for clause in cnf for lit in clause):
        raise ValueError("assignment shorter than variable id in CNF")

    for clause in cnf:
        satisfied = False
        for lit in clause:
            val = assignment[abs(lit) - 1]
            if (lit > 0 and val) or (lit < 0 and not val):
                satisfied = True
                break
        if not satisfied:
            return False

    return True
