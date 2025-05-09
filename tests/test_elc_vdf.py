import numpy as np
from landscape import generate_sat
from elc_vdf import (
    generate_phase_vdf,
    generate_phase_vdf_4d,
    verify_phase_vdf,
)

def test_roundtrip_1d():
    f = generate_sat(6, 2.0)
    cps = generate_phase_vdf(f, steps=20, lam=0.1, verify_gap=5)
    assert verify_phase_vdf(f, cps, lam=0.1, verify_gap=5)

def test_energy_monotone_1d():
    f = generate_sat(8, 1.5)
    cps = generate_phase_vdf(f, steps=30, lam=0.05, verify_gap=10)
    energies = [e for _, e in cps]
    assert energies == sorted(energies, reverse=True)

def test_roundtrip_4d():
    f = generate_sat(8, 2.0)
    cps = generate_phase_vdf_4d(f, steps=25, lam=0.1, verify_gap=5)
    assert verify_phase_vdf(f, cps, lam=0.1, verify_gap=5)

def test_energy_monotone_4d():
    f = generate_sat(7, 1.8)
    cps = generate_phase_vdf_4d(f, steps=20, lam=0.05, verify_gap=5)
    energies = [e for _, e in cps]
    assert energies == sorted(energies, reverse=True)
