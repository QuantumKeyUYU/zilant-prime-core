#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core Contributors
"""Atheris fuzzer for VDF functions."""

import sys

import atheris

from zilant_prime_core.vdf.vdf import generate_posw_sha256, verify_posw_sha256


def test_one_input(data: bytes) -> None:
    if not data:
        return
    steps = data[0] % 5 + 1
    seed = data[1:]
    proof = generate_posw_sha256(seed, steps)
    verify_posw_sha256(seed, proof, steps)


def main() -> None:
    atheris.Setup(sys.argv, test_one_input, enable_python_coverage=True)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
