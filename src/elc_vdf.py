import numpy as np

from landscape import energy  # реальная энергия из landscape


def gradient(formula, state, eps=1e-5):
    """
    Численный градиент энергии по состоянию state.
    energy может возвращать массив; используем скалярную сумму.
    """
    grad = np.zeros_like(state)
    for i in range(len(state)):
        orig = state[i]
        state[i] = orig + eps
        plus = np.sum(energy(formula, state))
        state[i] = orig - eps
        minus = np.sum(energy(formula, state))
        state[i] = orig
        grad[i] = (plus - minus) / (2 * eps)
    return grad


def generate_phase_vdf(formula, steps, lam, verify_gap=5):
    """
    Одномерный фазовый VDF-«заглушка»:
    — состояние не меняется (нулевой градиент)
    — энергия вычисляется как скаляр через сумму
    """
    cps = []
    state = np.zeros(len(formula), dtype=float)
    raw_e = energy(formula, state)
    # Если energy возвращает массив, суммируем его
    e = np.sum(raw_e)
    for step in range(1, steps + 1):
        cps.append((state.copy(), e))
        if step % verify_gap == 0:
            print(f"[1D Step {step}/{steps}] Energy: {e:.6f}")
    return cps


def generate_phase_vdf_4d(formula, steps, lam, verify_gap=5):
    """
    4D-фазовый VDF-«заглушка»:
    — состояние 4×N не меняется
    — энергия = сумма норм нулевого state = 0
    """
    cps = []
    state = np.zeros((4, len(formula)), dtype=float)
    # энергия нулевого состояния
    e = np.sum(np.linalg.norm(state, axis=0))
    for step in range(1, steps + 1):
        cps.append((state.copy(), e))
        if step % verify_gap == 0:
            print(f"[4D Step {step}/{steps}] Energy: {e:.6f}")
    return cps


def verify_phase_vdf(formula, cps, lam, verify_gap=5):
    """
    Проверка, что энергия не возрастает.
    """
    prev = float("inf")
    for i, (_, e) in enumerate(cps, start=1):
        if e > prev + 1e-12:
            print(f"Energy ↑ at checkpoint {i}: {e:.6f} > {prev:.6f}")
            return False
        prev = e
    return True
