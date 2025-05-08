import math

import hypothesis.strategies as st
from hypothesis import given, settings

from landscape import generate_sat
from elc_vdf import generate_phase_vdf, verify_phase_vdf


# ---------- property: round‑trip -----------
@given(
    n=st.integers(min_value=6, max_value=12),
    steps=st.integers(min_value=20, max_value=50),
    lam=st.floats(min_value=0.05, max_value=0.2),
)
@settings(max_examples=30, deadline=None)
def test_roundtrip(n, steps, lam):
    f = generate_sat(n)
    cps = generate_phase_vdf(f, steps, lam, verify_gap=10)
    assert verify_phase_vdf(f, cps, lam, verify_gap=10)


# ---------- property: энергия не возрастает -----------
def test_energy_monotone():
    f = generate_sat(10)
    cps = generate_phase_vdf(f, 40, 0.15)
    energies = [e for _, e in cps]
    assert energies == sorted(energies, reverse=True)


# ---------- verify быстрее generate -----------
def test_verify_faster_than_generate():
    f = generate_sat(8)
    steps = 100
    cps = generate_phase_vdf(f, steps, 0.2, verify_gap=10)

    # Обёртка-счётчик
    from landscape import compress as _orig

    class C:
        cnt = 0

    def _wrap(formula, lam):
        C.cnt += 1
        return _orig(formula, lam)

    import landscape

    landscape.compress, bak = _wrap, landscape.compress
    verify_phase_vdf
