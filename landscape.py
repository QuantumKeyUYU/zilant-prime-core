"""
Energy‑Landscape toolkit (prototype v0.1)

• generate_sat(n, density)        – случайная 3‑SAT формула
• energy(formula, assignment)     – # неудовлетворённых клауз
• compress(formula, λ)            – фазовое «сжатие» Σ_λ

Цель compress(): удалить λ‑долю «наиболее энергетически
вкладных» клауз, сохранив при этом валидные решения.

Метрика энергии = число неисполненных клауз
(lower = better).  Σ_λ просто отбрасывает верхние λ·m клауз
по усреднённой вкладу.
"""
from __future__ import annotations

import math
import random
from typing import List, Sequence, Tuple

Clause = Tuple[int, int, int]  # литералы как ±var_idx (1‑based)
Formula = List[Clause]


# ─────────────────────────────────────
# 1. генерация случайной 3‑SAT формулы
# ─────────────────────────────────────
def generate_sat(n_vars: int, density: float = 4.2) -> Formula:
    """
    :param n_vars: число переменных
    :param density: m / n коэффициент
    :return: список клауз длиной 3
    """
    m_clauses = math.ceil(density * n_vars)
    formula: Formula = []
    for _ in range(m_clauses):
        lits = set()
        while len(lits) < 3:
            var = random.randint(1, n_vars)
            sign = random.choice([-1, 1])
            lits.add(sign * var)
        formula.append(tuple(lits))  # type: ignore[arg-type]
    return formula


# ─────────────────────────────────────
# 2. энергия удовлетворения
# ─────────────────────────────────────
def _lit_value(lit: int, assign: Sequence[bool]) -> bool:
    idx = abs(lit) - 1
    val = assign[idx]
    return val if lit > 0 else (not val)


def energy(formula: Formula, assignment: Sequence[bool]) -> int:
    """
    :return: число неудовлетворённых клауз
    """
    unsat = 0
    for c in formula:
        if not (_lit_value(c[0], assignment) or _lit_value(c[1], assignment) or _lit_value(c[2], assignment)):
            unsat += 1
    return unsat


# ─────────────────────────────────────
# 3. фазовое «сжатие» Σ_λ
# ─────────────────────────────────────
def compress(formula: Formula, lam: float, sample: int = 128) -> Formula:
    """
    :param formula: исходная формула
    :param lam: 0 ≤ λ ≤ 1 – доля самого «дорогого» вклада, удаляемая
    :param sample: кол-во случайных назначений для оценки вклада клаузы
    :return: сжатая формула (подмножество исходной)
    """
    if not (0.0 <= lam <= 1.0):
        raise ValueError("λ must be in [0,1]")
    if lam == 0 or not formula:
        return list(formula)

    n_vars = max(abs(l) for clause in formula for l in clause)
    # считаем вклад каждой клаузы
    scores = [0] * len(formula)
    for _ in range(sample):
        a = [random.getrandbits(1) == 1 for _ in range(n_vars)]
        for idx, clause in enumerate(formula):
            if not (_lit_value(clause[0], a) or _lit_value(clause[1], a) or _lit_value(clause[2], a)):
                scores[idx] += 1

    # выбираем (1‑λ) самых «лёгких» клауз
    k_keep = max(1, int(math.ceil((1 - lam) * len(formula))))
    keep_idx = sorted(range(len(formula)), key=scores.__getitem__)[:k_keep]
    return [formula[i] for i in keep_idx]
