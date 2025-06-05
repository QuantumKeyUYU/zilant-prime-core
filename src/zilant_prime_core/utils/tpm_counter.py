import os
import subprocess

_MOCK_MODE = os.getenv("ZILANT_NO_TPM") == "1"


class TpmCounterError(Exception):
    pass


__all__ = ["read_tpm_counter", "increment_tpm_counter", "TpmCounterError"]


_counter_val = 0


def read_tpm_counter() -> int:
    """Read TPM counter value via tpm2_getcap or return a mock value."""
    global _counter_val
    if _MOCK_MODE:
        _counter_val += 1
        return _counter_val

    if subprocess.call(["which", "tpm2_getcap"], stdout=subprocess.DEVNULL) != 0:
        raise TpmCounterError("TPM utility not found")
    try:
        result = subprocess.run(
            ["tpm2_getcap", "properties-variable"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        out = result.stdout.decode()
        for line in out.splitlines():
            if "TPM_PT_PERSISTENT" in line:
                parts = line.split()
                return int(parts[-1], 0)
    except Exception as e:  # pragma: no cover - fallback
        raise TpmCounterError(f"Cannot read TPM counter: {e}")
    raise TpmCounterError("Unable to parse TPM counter")


def increment_tpm_counter() -> None:
    """Increment TPM counter via tpm2_increment or no-op in mock mode."""
    if _MOCK_MODE:
        return
    if (
        subprocess.call(
            [
                "which",
                "tpm2_increment",
            ],
            stdout=subprocess.DEVNULL,
        )
        != 0
    ):
        raise TpmCounterError("TPM increment utility not found")
    try:  # pragma: no cover - system call
        subprocess.run(["tpm2_increment", "0x81010001"], check=True)  # pragma: no cover - system call
    except Exception as e:  # pragma: no cover - system call
        raise TpmCounterError(f"Cannot increment TPM counter: {e}")
