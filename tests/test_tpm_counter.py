import pytest

from zilant_prime_core.utils.tpm_counter import get_and_increment_tpm_counter


class DummyResult:
    def __init__(self, returncode: int, stdout: bytes = b""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = b""


def test_counter_no_command(monkeypatch):
    monkeypatch.setattr("subprocess.run", lambda *a, **kw: (_ for _ in ()).throw(FileNotFoundError()))
    assert get_and_increment_tpm_counter() == 0


def test_counter_bad_output(monkeypatch):
    def fake_run(*args, **kwargs):
        return DummyResult(0, b"notint")

    monkeypatch.setattr("subprocess.run", fake_run)
    with pytest.raises(RuntimeError):
        get_and_increment_tpm_counter()


def test_counter_ok(monkeypatch):
    seq = [DummyResult(0, b"5"), DummyResult(0)]

    def fake_run(*args, **kwargs):
        return seq.pop(0)

    monkeypatch.setattr("subprocess.run", fake_run)
    assert get_and_increment_tpm_counter() == 6
