# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional


def attest_via_tpm() -> Optional[bool]:
    pcr_env = Path(os.environ.get("ZILANT_PCR_PATH", "/sys/class/tpm/tpm0/pcrs"))
    if shutil.which("tpm2_quote") is None:
        return None
    if not pcr_env.is_dir():
        return False
    local_values: dict[int, bytes] = {}
    for entry in pcr_env.iterdir():
        try:
            idx = int(entry.name)
            data = entry.read_bytes().strip()
            local_values[idx] = data
        except Exception:
            continue
    if not local_values:
        return False
    quote_file = Path(os.environ.get("ZILANT_QUOTE_FILE", "/tmp/tpm_quote.bin"))
    cmd_quote = [
        "tpm2_quote",
        "-C",
        os.environ.get("ZILANT_TPM_KEY_CTX", "0x81010001"),
        "-l",
        ",".join(str(i) for i in sorted(local_values.keys())),
        "-q",
        str(quote_file),
    ]
    result = subprocess.run(cmd_quote, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0 or not quote_file.exists():
        return False
    cmd_verify = [
        "tpm2_verifysignature",
        "-c",
        os.environ.get("ZILANT_TPM_PUBKEY_CTX", "0x81010002"),
        "-m",
        str(quote_file),
        "-s",
        f"{quote_file}.sig",
    ]
    result_verify = subprocess.run(cmd_verify, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result_verify.returncode == 0
