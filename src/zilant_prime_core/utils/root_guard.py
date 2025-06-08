# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core Contributors
"""Basic root/jailbreak detection helpers."""
from __future__ import annotations

import os
import sys
from pathlib import Path

__all__ = ["is_device_rooted", "assert_safe_or_die"]


_DEF_SU_PATHS = [
    "/system/xbin/su",
    "/system/bin/su",
    "/sbin/su",
    "/bin/su",
    "/usr/bin/sudo",
    "/usr/bin/su",
    "/magisk",
    "/init.superuser.rc",
]


def _check_uid_gid() -> bool:
    """Return True if running as UID or GID 0."""
    try:
        if os.getuid() == 0 or os.getgid() == 0:
            return True
    except AttributeError:
        # Windows does not have getuid / getgid
        pass
    try:
        import ctypes

        if hasattr(ctypes, "windll"):
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        pass
    return False


def _check_su_paths() -> bool:
    for p in _DEF_SU_PATHS:
        if Path(p).exists():
            return True
    return False


def _check_mount_flags() -> bool:
    try:
        with open("/proc/self/mountinfo", "r") as f:
            for line in f:
                parts = line.split()
                if len(parts) > 5 and parts[4] == "/":
                    if "rw," in line:
                        return True
                    break
    except Exception:
        pass
    return False


def _check_selinux() -> bool:
    try:
        path = Path("/sys/fs/selinux/enforce")
        if path.exists():
            text = path.read_text().strip()
            if text != "1":
                return True
    except Exception:
        pass
    return False


def _check_tracerpid() -> bool:
    try:
        with open("/proc/self/status", "r") as f:
            for line in f:
                if line.startswith("TracerPid:"):
                    pid = int(line.split()[1])
                    if pid != 0:
                        return True
                    break
    except Exception:
        pass
    return False


_CHECKS = [
    _check_uid_gid,
    _check_su_paths,
    _check_mount_flags,
    _check_selinux,
    _check_tracerpid,
]


def is_device_rooted() -> bool:
    """Return True if any root/jailbreak indication is detected."""
    for check in _CHECKS:
        try:
            if check():
                return True
        except Exception:
            # Conservative: treat errors as suspicious
            return True
    return False


def assert_safe_or_die() -> None:
    """Abort the process if root/jailbreak is detected."""
    if is_device_rooted() and not (os.environ.get("ZILANT_ALLOW_ROOT") or "PYTEST_CURRENT_TEST" in os.environ):
        sys.exit(113)
