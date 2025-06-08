# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

__version__ = "0.3.0"

# Basic runtime root/jailbreak guard.
from .utils import root_guard

root_guard.assert_safe_or_die()

# Hello, Zilant!
# ZILANT PRIME TEST 12345
