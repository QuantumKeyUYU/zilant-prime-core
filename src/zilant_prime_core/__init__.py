# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

__version__ = "0.1.1"

__all__: list[str] = ["cli", "utils", "vdf"]

import os

if not os.environ.get("ZILANT_TESTING"):
    from .cli import _abort  # NoReturn

    _abort("Unsafe import before guard!", code=99)  # pragma: no cover

from .utils import root_guard

if not os.environ.get("ZILANT_ALLOW_ROOT"):
    root_guard.assert_safe_or_die()
root_guard.harden_linux()

# Hello, Zilant!
# ZILANT PRIME TEST 12345
