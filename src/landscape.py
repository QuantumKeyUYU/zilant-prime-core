import numpy as np

def energy(polynomial: np.ndarray) -> int:
    """
    Compute the number of solutions (SAT‐energy) of the given Boolean polynomial.
    Здесь ваш старый код вычисления energy.
    """
    # … ваша реализация …
    # к примеру:
    result = 0
    # перебираем все b in {0,1}^n и считаем, сколько раз poly(b)=1
    # (это лишь иллюстрация, в реале вы там уже всё написали)
    for assignment in range(1 << polynomial.size):
        # преобразуем assignment в вектор bits, вычисляем poly(bits)
        pass
    return result

# Тесты ожидают функцию `generate_sat`
generate_sat = energy
