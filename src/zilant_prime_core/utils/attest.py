"""TPM attestation stub."""

import subprocess
import sys


def attest_via_tpm() -> None:  # pragma: no cover
    """Заглушка Stage 0: если tpm2_quote не найден, просто пропускаем."""
    try:
        res = subprocess.run(
            [
                "tpm2_quote",
                "--key-context",
                "key.ctx",
                "--pcr-list",
                "0,1",
                "--message-pcr",
                "pcr_values.bin",
                "--signature",
                "signature.bin",
            ],
            capture_output=True,
        )
        if res.returncode != 0:
            print("Remote Attestation failed: cannot get quote", file=sys.stderr)
            sys.exit(1)
    except FileNotFoundError:
        print("Local mode: TPM not available, skipping attestation")
