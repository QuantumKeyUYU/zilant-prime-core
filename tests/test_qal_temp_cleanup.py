from zilant_prime_core.utils.qal import QAL


def test_qal_verify_does_not_leave_tmp(tmp_path):
    # Подготовка: создаём рабочую папку и экземпляр QAL
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    qal = QAL(3, work_dir)
    message = b"test-message"
    pubkeys = [pub.read_bytes() for _, pub in qal.keys]

    # Сохраняем список файлов до вызова verify
    before = set(work_dir.iterdir())

    # Вызываем verify (нам важно, чтобы временные файлы убрались)
    _ = qal.verify(message, b"", pubkeys)

    # Сохраняем список файлов после и сравниваем
    after = set(work_dir.iterdir())
    assert before == after, "QAL.verify оставил временные файлы"
