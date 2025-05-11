import numpy as np
from scipy.optimize import minimize

def potential_energy(x):
    return np.sum(x**2)

def optimize_landscape(n=10):
    x0 = np.random.rand(n)
    result = minimize(potential_energy, x0)
    return result

if __name__ == "__main__":
    result = optimize_landscape()
    print("Optimization result:", result)
