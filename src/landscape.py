def generate_sat(n_vars: int, density: float):
    """
    Dummy SAT-generator for tests.
    Returns a simple tuple that represents the formula.
    """
    if not isinstance(n_vars, int) or n_vars <= 0:
        raise ValueError("n_vars must be a positive integer.")
    if not isinstance(density, (int, float)) or density <= 0:
        raise ValueError("density must be positive.")
    return (n_vars, density)
