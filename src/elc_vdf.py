"""
Phase‑VDF (Energy‑Landscape) — прототип v0.1

 Идея:
   • Итерация = фазовое сжатие Σ_λ (landscape.compress).
   • Чек‑пойнт = (step_idx, energy_after_allFalse).
   • Verify = пересчитываем compress только для check‑point'ов,
              поэтому время ≈ steps / verify_gap << steps.

 Главное свойство (для прототипа):
   энергия не возрастает (non‑increasing).

 API:
   generate_phase_vdf(formula, steps, λ, verify_gap=10) -> [Checkpoint]
   verify_phase_vdf(formula, checkpoints, λ, verify_gap=10) -> bool
"""
from __future__ import annotations

from typing import List, Tuple

from landscape import compress, energy, Formula

Checkpoint = Tuple[int, int]  # (step_idx, energy_val)


# ─────────────────────────  генерация  ─────────────────────────
def generate_phase_vdf(
    formula: Formula,
    steps: int,
    lam: float,
    verify_gap: int = 10,
) -> List[Checkpoint]:
    if steps < 1:
        raise ValueError("steps must be ≥1")
    if not (0.0 < lam <= 0.5):
        raise ValueError("λ should be (0, 0.5]")
    if verify_gap < 1:
        raise ValueError("verify_gap must be ≥1")

    checkpoints: List[Checkpoint] = []
    cur = formula
    for i in range(steps):
        cur = compress(cur, lam)
        if i % verify_gap == 0 or i == steps - 1:
            e = energy(cur, [False] * 32)  # deterministic cheap proxy
            checkpoints.append((i, e))
    return checkpoints


# ─────────────────────────  проверка  ─────────────────────────
def verify_phase_vdf(
    formula: Formula,
    checkpoints: List[Checkpoint],
    lam: float,
    verify_gap: int = 10,
) -> bool:
    if not checkpoints:
        return False
    if lam <= 0 or verify_gap < 1:
        return False

    cur = formula
    idx_now = 0
    for step, want_e in checkpoints:
        while idx_now <= step:
            cur = compress(cur, lam)
            idx_now += 1
        have_e = energy(cur, [False] * 32)
        if have_e != want_e:
            return False

    energies = [e for _, e in checkpoints]
    # non‑increasing
    return energies == sorted(energies, reverse=True)
