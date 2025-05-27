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

    return True
