# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

"""
Stub for the built-in `_winapi` module on non-Windows platforms,
so that import _winapi succeeds and CopyFile2 can be monkey-patched in tests.
"""


def CopyFile2(src, dst, flags=0, progress=None):
    """
    Stub implementation of CopyFile2.
    On non-Windows platforms this will simply raise if ever called
    without being monkeypatched in tests.
    """
    raise NotImplementedError("CopyFile2 is not implemented on this platform")
