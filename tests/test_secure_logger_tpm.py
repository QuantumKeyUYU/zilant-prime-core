# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

import os
import subprocess
import shutil

from zilant_prime_core.utils.secure_logging import SecureLogger


def test_secure_logger_fetches_tpm_key(monkeypatch, tmp_path):
    calls = {}

    def fake_which(cmd):
        return "/usr/bin/tpm2_getrandom" if cmd == "tpm2_getrandom" else None

    def fake_check_output(args, timeout=5):
        calls["args"] = args
        return b"x" * 32

    monkeypatch.setattr(shutil, "which", fake_which)
    monkeypatch.setattr(subprocess, "check_output", fake_check_output)
    monkeypatch.delenv("ZILANT_LOG_KEY", raising=False)

    slog = SecureLogger(log_path=str(tmp_path / "tpm.log"))
    assert calls["args"] == ["tpm2_getrandom", "32"]
    slog.log("hi")
    assert slog.read_logs() == [("INFO", "hi")]
