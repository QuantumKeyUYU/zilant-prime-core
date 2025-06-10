# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

__version__ = "0.1.0"

import os

from .utils import root_guard

if not os.environ.get("ZILANT_ALLOW_ROOT"):
    root_guard.assert_safe_or_die()
root_guard.harden_linux()

# Hello, Zilant!
# ZILANT PRIME TEST 12345
