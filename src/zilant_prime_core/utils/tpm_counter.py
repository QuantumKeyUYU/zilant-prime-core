from __future__ import annotations

import subprocess

__all__ = ["get_and_increment_tpm_counter"]


def get_and_increment_tpm_counter() -> int | None:
    try:
        res_read = subprocess.run(
            ["tpm2_getcounter", "--object-context", "0x01500020"],
            capture_output=True,
            text=True,
        )
        if res_read.returncode != 0:
            return 0
        current = int(res_read.stdout.strip())
        res_inc = subprocess.run(
            ["tpm2_incrementcounter", "--object-context", "0x01500020", "--auth=sys"],
            capture_output=True,
        )
        if res_inc.returncode != 0:
            raise RuntimeError("Cannot increment TPM counter")
        return current + 1
    except FileNotFoundError:
        return 0
    except Exception as e:
        raise RuntimeError(f"TPM counter error: {e}") from e
