import pytest

from zilant_prime_core.crypto.aead import AEADInvalidTagError
from zilant_prime_core.phase import QuantumPhaseCipher, generate_phase_key, hardware_fingerprint


def test_phase_key_unique():
    k1 = generate_phase_key()
    k2 = generate_phase_key()
    assert k1 != k2
    assert len(k1) == len(k2) == 32


def test_cipher_roundtrip():
    cipher = QuantumPhaseCipher()
    data = b"secret payload"
    blob = cipher.encrypt(data)
    assert cipher.decrypt(blob) == data


def test_cipher_failure_increases_complexity():
    cipher = QuantumPhaseCipher(complexity=1)
    good = cipher.encrypt(b"data")
    bad = bytearray(good)
    bad[-1] ^= 0xFF
    with pytest.raises(AEADInvalidTagError):
        cipher.decrypt(bytes(bad))
    assert cipher.complexity > 1
    # encrypt/decrypt again to reset complexity
    blob = cipher.encrypt(b"again")
    assert cipher.decrypt(blob) == b"again"
    assert cipher.complexity == 32


def test_hardware_fingerprint_stable(monkeypatch):
    fp1 = hardware_fingerprint()
    fp2 = hardware_fingerprint()
    assert fp1 == fp2 and len(fp1) == 32
