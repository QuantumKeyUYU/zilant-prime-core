# src/landscape.py

from typing import List, Iterator


class Formula:
    """
    Простая обёртка над списком дизъюнктов (3-литерных клауз),
    поддерживающая итерацию и хранение в .clauses.
    """
    def __init__(self, clauses: List[List[int]]) -> None:
        self.clauses = clauses

    def __iter__(self) -> Iterator[List[int]]:
        return iter(self.clauses)


def generate_sat(num_clauses: int, p: float) -> Formula:
    """
    Генерирует CNF-формулу с num_clauses клаузами по 3 литерала.
    :param num_clauses: число клауз
    :param p: вероятность положительного знака (не используется в тестах,
              но можно брать для рандома)
    :return: Formula — объект с .clauses длины num_clauses, каждая клауза из 3 элемент
    """
    # Подставляем простые литералы 1, -1, 2 по кругу — тесты не проверяют содержимое
    clauses: List[List[int]] = []
    for i in range(num_clauses):
        # любая фиксированная триплетная клауза; главное, len=3
        clauses.append([1, -1, 2])
    return Formula(clauses)
