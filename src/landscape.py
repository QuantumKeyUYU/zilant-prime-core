import numpy as np
from scipy.optimize import minimize

def potential_energy(x: np.ndarray) -> float:
    return float(np.dot(x, x))

def optimize_landscape(dim: int = 10):
    x0 = np.random.rand(dim)
    res = minimize(potential_energy, x0)
    return res

if __name__ == "__main__":
    result = optimize_landscape()
    print("Result:", result)
