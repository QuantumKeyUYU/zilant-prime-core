import pytest

from zilant_prime_core.utils.tpm_counter import TpmCounterError, read_tpm_counter


def test_read_tpm_counter_no_utility(monkeypatch):
    monkeypatch.setattr("subprocess.call", lambda *args, **kwargs: 1)
    with pytest.raises(TpmCounterError):
        read_tpm_counter()


def test_read_tpm_counter_parse(monkeypatch):
    class DummyResult:
        def __init__(self, stdout: bytes):
            self.stdout = stdout

    fake_output = b"\n    handle: 0x81010001, TPM_PT_PERSISTENT: 0x5\n    "
    monkeypatch.setattr("subprocess.call", lambda *a, **k: 0)
    monkeypatch.setattr("subprocess.run", lambda *a, **k: DummyResult(fake_output))
    assert read_tpm_counter() == 5


def test_read_tpm_counter_parse_fail(monkeypatch):
    class DummyResult:
        def __init__(self, stdout: bytes):
            self.stdout = stdout

    fake_output = b"NOTHING HERE"
    monkeypatch.setattr("subprocess.call", lambda *a, **k: 0)
    monkeypatch.setattr("subprocess.run", lambda *a, **k: DummyResult(fake_output))
    with pytest.raises(TpmCounterError):
        read_tpm_counter()
