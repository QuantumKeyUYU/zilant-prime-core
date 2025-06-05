# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

"""Wrapper for hardening shared library."""

from __future__ import annotations

from ctypes import CDLL
from pathlib import Path

LIB = CDLL(str(Path(__file__).with_name("hardening_rt.so")))


def apply_runtime_hardening() -> None:
    LIB.apply_runtime_hardening()
