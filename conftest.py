# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

import sys
from pathlib import Path

# вставляем папку src/ в начало sys.path, чтобы
# import zilant_prime_core… брал код именно из src/
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if SRC.is_dir():
    sys.path.insert(0, str(SRC))


import tempfile

import pytest


@pytest.fixture(autouse=True)
def _patch_tpm_counter(monkeypatch):
    counter = {"val": 0}

    def fake_read() -> int:
        counter["val"] += 1
        return counter["val"]

    monkeypatch.setattr("zilant_prime_core.utils.tpm_counter.read_tpm_counter", fake_read)
    monkeypatch.setattr("zilant_prime_core.utils.attest.attest_via_tpm", lambda: None)
    try:
        import zilant_prime_core.cli as cli_mod

        monkeypatch.setattr(cli_mod, "read_tpm_counter", fake_read)
        monkeypatch.setattr(cli_mod, "attest_via_tpm", lambda: None)
        cli_mod._pack_rate_limiter._calls.clear()
    except Exception:
        pass
    tmp_home = tempfile.mkdtemp(prefix="home")
    monkeypatch.setenv("HOME", tmp_home)
