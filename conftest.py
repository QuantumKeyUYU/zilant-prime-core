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
def _setup_env(monkeypatch):
    try:
        import zilant_prime_core.cli as cli_mod
        cli_mod._pack_rate_limiter._calls.clear()
    except Exception:
        pass
    tmp_home = tempfile.mkdtemp(prefix="home")
    monkeypatch.setenv("HOME", tmp_home)
