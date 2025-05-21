# landscape.py
import random
from typing import List


def generate_sat(variables: int, density: float) -> List[List[int]]:
    """
    Builds a random 3-CNF formula:
      - variables: number of variables (must be >0)
      - density: approximate clauses-per-variable
    """
    if not isinstance(variables, int) or variables <= 0:
        raise ValueError("Number of variables must be a positive integer.")
    if not isinstance(density, (int, float)) or density < 0:
        raise ValueError("Density must be non-negative.")
    num_clauses = int(variables * density)
    formula = []
    for _ in range(num_clauses):
        # pick up to 3 distinct variable indices
        picks = random.sample(range(1, variables + 1), k=min(3, variables))
        clause = []
        for v in picks:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        formula.append(clause)
    return formula
