import math
from typing import List

import hypothesis.strategies as st
from hypothesis import given, settings

from landscape import compress, energy, generate_sat


@given(
    n=st.integers(min_value=5, max_value=12),
    density=st.floats(min_value=3.5, max_value=5.0),
    lam=st.floats(min_value=0.0, max_value=0.6),
)
@settings(max_examples=50, deadline=None)
def test_compress_energy_monotone(n: int, density: float, lam: float):
    formula = generate_sat(n, density)
    comp = compress(formula, lam)

    # случайное назначение
    a = [False] * n
    e_orig = energy(formula, a)
    e_comp = energy(comp, a)

    assert e_comp <= e_orig  # сжатие не ухудшает энергию


@given(
    n=st.integers(min_value=5, max_value=10),
    lam=st.floats(min_value=0.2, max_value=0.8),
)
def test_compress_size_reduces(n: int, lam: float):
    f = generate_sat(n)
    c = compress(f, lam)
    assert 1 <= len(c) <= len(f)
    # ожидаем уменьшение при положительном λ
    if lam > 0:
        assert len(c) < len(f)


def test_generate_sat_structure():
    f = generate_sat(8, 4.0)
    assert all(len(cl) == 3 for cl in f)
    assert all(isinstance(l, int) for cl in f for l in cl)
    vars_used: List[int] = [abs(l) for cl in f for l in cl]
    assert max(vars_used) <= 8
