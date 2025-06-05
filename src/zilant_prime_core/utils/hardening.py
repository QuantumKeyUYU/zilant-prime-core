# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

"""Wrapper for hardening shared library."""

from __future__ import annotations

import os
from ctypes import CDLL
from pathlib import Path

LIB = None
if os.getenv("DISABLE_HARDENING") != "1":
    try:
        LIB = CDLL(str(Path(__file__).with_name("hardening_rt.so")))
    except OSError:
        # Hardening library isn't available; continue without it
        LIB = None


def apply_runtime_hardening() -> None:
    if LIB is not None:
        LIB.apply_runtime_hardening()
