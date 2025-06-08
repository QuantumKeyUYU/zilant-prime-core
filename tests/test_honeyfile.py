import pytest

from zilant_prime_core.utils.honeyfile import HoneyfileError, check_tmp_for_honeyfiles


def test_detect_honeyfile(tmp_path):
    f = tmp_path / "secret.doc"
    f.write_text("x")
    with pytest.raises(HoneyfileError):
        check_tmp_for_honeyfiles(tmp_path)


def test_no_honeyfile(tmp_path):
    (tmp_path / "normal.txt").write_text("d")
    check_tmp_for_honeyfiles(tmp_path)
