import pytest
from landscape import generate_sat, Formula


def test_generate_sat_structure():
    f = generate_sat(8, 1.0)
    assert isinstance(f, Formula)
    assert all(len(cl) == 3 for cl in f.clauses)
    assert len(f.clauses) == 8


def test_formula_iteration():
    f = generate_sat(5, 1.0)
    assert len(list(f)) == 5
    assert all(len(cl) == 3 for cl in f)
