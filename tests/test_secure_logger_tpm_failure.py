# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

import shutil
import subprocess
import pytest

from zilant_prime_core.utils.secure_logging import SecureLogger


def test_secure_logger_tpm_error(monkeypatch, tmp_path):
    def fake_which(cmd):
        return "/usr/bin/tpm2_getrandom" if cmd == "tpm2_getrandom" else None

    def fake_check_output(args, timeout=5):
        raise RuntimeError("tpm error")

    monkeypatch.setattr(shutil, "which", fake_which)
    monkeypatch.setattr(subprocess, "check_output", fake_check_output)
    monkeypatch.delenv("ZILANT_LOG_KEY", raising=False)

    with pytest.raises(ValueError):
        SecureLogger(log_path=str(tmp_path / "tpm.log"))
