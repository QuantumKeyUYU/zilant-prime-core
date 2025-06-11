# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

__version__ = "0.1.1"

__all__: list[str] = ["cli", "utils", "vdf"]

import os

if os.getenv("ZILANT_ALLOW_ROOT") != "1":  # pragma: no cover
    from .cli import _abort  # NoReturn  # pragma: no cover

    _abort("Unsafe import before guard!", code=99)  # pragma: no cover

from .utils import root_guard

if os.getenv("ZILANT_ALLOW_ROOT") != "1":  # pragma: no cover
    root_guard.assert_safe_or_die()  # pragma: no cover
root_guard.harden_linux()

# Hello, Zilant!
# ZILANT PRIME TEST 12345
