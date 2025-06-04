import subprocess


def attestation_check():
    try:
        subprocess.run(
            ["tpm2_quote", "-C", "key.ctx", "-L", "sha256:0,1", "-o", "pcr_values.bin", "-q", "signature.bin"],
            check=True,
        )
        subprocess.run(
            ["tpm2_verifysignature", "-c", "key.pub", "-m", "pcr_values.bin", "-s", "signature.bin"],
            check=True,
        )
        return True
    except FileNotFoundError:
        print("TPM утилиты отсутствуют, локальный режим")
        return False
    except subprocess.CalledProcessError as exc:  # pragma: no cover - raised in tests
        raise RuntimeError("Attestation failed") from exc
