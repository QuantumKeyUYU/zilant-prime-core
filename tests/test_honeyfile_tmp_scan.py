import pytest

from zilant_prime_core.utils.honeyfile import HoneyfileError, check_tmp_for_honeyfiles, create_honeyfile


def test_honeyfile_detection_and_cleanup(tmp_path, monkeypatch):
    # monkeypatch чтобы check_tmp_for_honeyfiles смотрел в tmp_path
    monkeypatch.setenv("TMPDIR", str(tmp_path))

    # создаём “мёдовый” файл в tmp_path
    honey = tmp_path / "honey.txt"
    create_honeyfile(str(honey))

    # при сканировании должна бросаться ошибка
    with pytest.raises(HoneyfileError):
        check_tmp_for_honeyfiles()

    # удаляем файл и проверяем, что теперь ошибок нет
    honey.unlink()
    check_tmp_for_honeyfiles()  # не должно бросать
