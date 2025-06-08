#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core Contributors
"""Atheris fuzzer for AEAD encrypt/decrypt."""

import sys

import atheris

from zilant_prime_core.crypto.aead import decrypt_aead, encrypt_aead, generate_nonce


def test_one_input(data: bytes) -> None:
    if len(data) < 32:
        return
    key = data[:32]
    nonce = generate_nonce()
    msg = data[32:]
    ct = encrypt_aead(key, nonce, msg)
    try:
        decrypt_aead(key, nonce, ct)
    except Exception:
        pass


def main() -> None:
    atheris.Setup(sys.argv, test_one_input, enable_python_coverage=True)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
