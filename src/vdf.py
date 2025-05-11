import hashlib


def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def generate_vdf(seed: bytes, steps: int) -> bytes:
    """
    Генерирует полное VDF-доказательство.

    :param seed: Начальные данные.
    :param steps: Количество шагов итерации.
    :return: Финальный хеш после шагов.
    """
    result = seed
    for _ in range(steps):
        result = sha256(result)
    return result


def generate_partial_proofs(seed: bytes, steps: int, interval: int) -> dict:
    """
    Генерирует промежуточные доказательства каждые 'interval' шагов.

    :param seed: Начальные данные.
    :param steps: Общее число шагов.
    :param interval: Интервал для промежуточных доказательств.
    :return: Словарь {step_number: proof}.
    """
    result = seed
    proofs = {0: seed}
    for step in range(1, steps + 1):
        result = sha256(result)
        if step % interval == 0 or step == steps:
            proofs[step] = result
    return proofs


def verify_partial_proof(start_proof: bytes, end_proof: bytes, steps: int) -> bool:
    """
    Проверяет, что от начального до конечного доказательства ровно steps шагов.

    :param start_proof: Начальное доказательство.
    :param end_proof: Конечное доказательство.
    :param steps: Количество шагов между ними.
    :return: True, если доказательство корректно.
    """
    current = start_proof
    for _ in range(steps):
        current = sha256(current)
    return current == end_proof
