# root_guard.py
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
"""Simple root / jailbreak detection helpers."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Iterable

__all__ = ["is_device_rooted", "assert_safe_or_die"]

_ROOT_INDICATORS: Iterable[str] = (
    "/system/xbin/su",
    "/system/bin/su",
    "/system/app/Superuser.apk",
    "/sbin/su",
    "/system/bin/.ext/.su",
    "/system/usr/we-need-root/su",
    "/system/app/Kinguser.apk",
    "/data/local/bin/su",
    "/data/local/xbin/su",
    "/data/local/su",
    "/su/bin/su",
    "/magisk",
)


def _check_ld_preload() -> bool:  # pragma: no cover
    return bool(os.environ.get("LD_PRELOAD"))


def _check_uid_gid() -> bool:  # pragma: no cover
    return os.geteuid() == 0 or os.getegid() == 0 if hasattr(os, "geteuid") else False


def _check_root_binaries() -> bool:  # pragma: no cover
    for p in _ROOT_INDICATORS:
        if Path(p).exists():
            return True
    return False


def _check_mounts() -> bool:  # pragma: no cover
    try:
        with open("/proc/self/mountinfo", "r") as fh:
            for line in fh:
                if " rw," in line.split()[-1]:
                    if "/" in line.split()[4]:
                        return False
    except Exception:
        pass
    return False


def _check_selinux() -> bool:  # pragma: no cover
    path = Path("/sys/fs/selinux/enforce")
    try:
        if path.exists() and path.read_text().strip() != "1":
            return True
    except Exception:
        pass
    return False


def _check_ptrace() -> bool:  # pragma: no cover
    try:
        with open("/proc/self/status", "r") as fh:
            for line in fh:
                if line.startswith("TracerPid:"):
                    pid = int(line.split()[1])
                    return pid != 0
    except Exception:
        pass
    return False


def is_device_rooted() -> bool:
    """Return True if current environment appears to be rooted/jailbroken."""
    if _check_uid_gid():
        return True
    if _check_root_binaries():
        return True
    if _check_mounts():
        return True
    if _check_selinux():
        return True
    if _check_ptrace():
        return True
    if _check_ld_preload():
        return True
    return False


def assert_safe_or_die() -> None:
    """Exit the process if running on a rooted device."""
    if is_device_rooted():
        sys.stderr.write("Root environment detected. Aborting.\n")
        sys.stderr.flush()
        sys.exit(99)
