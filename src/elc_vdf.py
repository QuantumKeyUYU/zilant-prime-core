from typing import Any, List, Tuple

from landscape import compress, energy, Formula

def phase_transition(f: Formula, lam: float) -> Formula:
    """
    One deterministic Phase-VDF step:
    compress the landscape instance into a new state
    whose energy is guaranteed <= the old one.
    """
    new = compress(f, lam)
    e_old = energy(f, lam)
    e_new = energy(new, lam)
    assert e_new <= e_old, f"Energy must not increase: {e_new} > {e_old}"
    return new

def generate_phase_vdf(
    f: Formula,
    steps: int,
    lam: float,
    verify_gap: int = 1
) -> List[Tuple[int, float]]:
    """
    Run `steps` iterations of the Phase-VDF.
    Every `verify_gap` steps record a checkpoint (step, energy).
    """
    cur = f
    cps: List[Tuple[int, float]] = []
    for i in range(1, steps + 1):
        cur = phase_transition(cur, lam)
        if i % verify_gap == 0:
            e = energy(cur, lam)
            cps.append((i, e))
    return cps

def verify_phase_vdf(
    f: Any,
    cps: List[Tuple[int, float]],
    lam: float,
    verify_gap: int = 1
) -> bool:
    """
    Replay the VDF: starting from `f`, perform `phase_transition` in chunks of
    `verify_gap` steps, and check that each recorded energy matches the true
    energy (within a tiny tolerance).
    """
    cur = f
    tol = 1e-9
    for step, claimed_e in cps:
        # advance by verify_gap steps
        for _ in range(verify_gap):
            cur = phase_transition(cur, lam)
        actual_e = energy(cur, lam)
        if abs(actual_e - claimed_e) > tol:
            return False
    return True
