import random
from typing import List, Tuple


Clause = Tuple[int, int, int]


class Formula:
    def __init__(self, n: int, clauses: List[Clause]):
        self.n = n
        self.clauses = clauses

    def __iter__(self):
        return iter(self.clauses)

    def __len__(self):
        return len(self.clauses)


def generate_sat(n: int, density: float = 4.0) -> Formula:
    num_clauses = max(1, int(n * density))
    clauses = set()

    # Генерируем уникальные клаузы
    while len(clauses) < num_clauses:
        clause = tuple(sorted(random.randint(1, n) for _ in range(3)))
        if clause not in clauses and len(set(clause)) == 3:
            clauses.add(clause)

    return Formula(n, list(clauses))


def compress(formula: Formula, lam: float) -> Formula:
    # Простейший вариант — просто возвращаем исходную формулу
    return formula


def energy(formula: Formula, lam: float) -> float:
    """
    Энергия Σ_λ: число несатисфied клауз при all-false + λ * число клауз.
    """
    m = len(formula.clauses)
    unsat = sum(1 for clause in formula.clauses if not any(lit > 0 for lit in clause))
    return unsat + lam * m
