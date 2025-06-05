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

import subprocess


def pytest_configure(config):
    build_dir = SRC / "zilant_prime_core" / "utils"
    subprocess.run(
        ["gcc", "-fPIC", "-shared", "crypto_core.c", "-o", "crypto_core.so", "-lcrypto"], cwd=build_dir, check=True
    )
    try:
        subprocess.run(
            ["gcc", "-fPIC", "-shared", "hardening.c", "-o", "hardening_rt.so", "-lseccomp"],
            cwd=build_dir,
            check=True,
        )
    except subprocess.CalledProcessError:
        # Library may be missing; tests will no-op hardening
        print("Warning: failed to build hardening.so; continuing without")
