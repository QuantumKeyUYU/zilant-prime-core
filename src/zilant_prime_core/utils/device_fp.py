# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
"""Device fingerprint helpers for Quantum-Pseudo-HSM."""

from __future__ import annotations

import json
import os
import platform
import subprocess
import time
import uuid
from typing import Dict, cast

from crypto_core import hash_sha3
from utils.secure_memory import wipe_bytes

SALT_CONST: bytes = b"\x00" * 16


def collect_hw_factors() -> Dict[str, str]:
    """Return a dictionary of hardware factors for this device."""
    factors: Dict[str, str] = {}

    try:
        factors["cpu_processor"] = platform.processor() or ""
    except Exception:  # pragma: no cover - platform failure
        factors["cpu_processor"] = ""

    try:
        factors["machine"] = platform.machine() or ""
    except Exception:  # pragma: no cover - platform failure
        factors["machine"] = ""

    try:
        factors["platform"] = platform.platform() or ""
    except Exception:  # pragma: no cover - platform failure
        factors["platform"] = ""

    try:
        factors["python_version"] = platform.python_version()
    except Exception:  # pragma: no cover - platform failure
        factors["python_version"] = ""

    try:
        factors["node_name"] = platform.node() or ""
    except Exception:  # pragma: no cover - platform failure
        factors["node_name"] = ""

    try:
        factors["mac_address"] = format(uuid.getnode(), "x")
    except Exception:  # pragma: no cover - platform failure
        factors["mac_address"] = ""

    try:
        if platform.system().lower().startswith("win"):
            output = (
                subprocess.check_output(["wmic", "csproduct", "get", "UUID"], stderr=subprocess.DEVNULL)
                .decode(errors="ignore")
                .splitlines()
            )
            uuid_win = ""
            for line in output:
                line = line.strip()
                if line and "UUID" not in line:
                    uuid_win = line
                    break
            factors["smbios_uuid"] = uuid_win
        else:
            factors["smbios_uuid"] = ""
    except Exception:  # pragma: no cover - command failure
        factors["smbios_uuid"] = ""

    try:
        if platform.system().lower().startswith("win"):
            output = (
                subprocess.check_output(["wmic", "bios", "get", "SMBIOSBIOSVersion"], stderr=subprocess.DEVNULL)
                .decode(errors="ignore")
                .splitlines()
            )
            bios_ver = ""
            for line in output:
                line = line.strip()
                if line and "SMBIOSBIOSVersion" not in line:
                    bios_ver = line
                    break
            factors["bios_version"] = bios_ver
        else:
            try:
                with open(
                    "/sys/class/dmi/id/bios_version",
                    "r",
                ) as f:  # pragma: no cover - system specific
                    factors["bios_version"] = f.read().strip()
            except Exception:  # pragma: no cover - access failure
                factors["bios_version"] = ""
    except Exception:  # pragma: no cover - command failure
        factors["bios_version"] = ""

    try:
        if platform.system().lower().startswith("win"):
            output = (
                subprocess.check_output(["wmic", "diskdrive", "get", "SerialNumber"], stderr=subprocess.DEVNULL)
                .decode(errors="ignore")
                .splitlines()
            )
            ds = ""
            for line in output:
                line = line.strip()
                if line and "SerialNumber" not in line:
                    ds = line
                    break
            factors["disk_serial"] = ds
        else:
            try:
                output = (
                    subprocess.check_output(["lsblk", "-o", "SERIAL", "-dn"], stderr=subprocess.DEVNULL)
                    .decode(errors="ignore")
                    .splitlines()
                )
                factors["disk_serial"] = output[0].strip() if output else ""
            except Exception:  # pragma: no cover - lsblk failure
                factors["disk_serial"] = ""
    except Exception:  # pragma: no cover - command failure
        factors["disk_serial"] = ""

    try:
        factors["cpu_count"] = str(os.cpu_count() or "")
    except Exception:  # pragma: no cover - os error
        factors["cpu_count"] = ""

    try:
        t = time.time()
        time.sleep(0.001)
        factors["entropy_jitter"] = f"{t}"
    except Exception:  # pragma: no cover - time failure
        factors["entropy_jitter"] = ""

    try:
        import psutil  # pragma: no cover - optional

        nics = list(psutil.net_if_addrs().keys())  # pragma: no cover - optional
        factors["network_interfaces"] = json.dumps(nics, ensure_ascii=False)  # pragma: no cover - optional
    except Exception:  # pragma: no cover - psutil not available
        factors["network_interfaces"] = ""

    factors["dummy_factor"] = "zilant"

    return factors


def compute_fp(hw: Dict[str, str], salt: bytes) -> bytes:
    """Return SHA3-256 fingerprint for ``hw`` dictionary and ``salt``."""
    if not isinstance(hw, dict):
        raise TypeError("hw must be dict[str, str]")
    if not isinstance(salt, (bytes, bytearray)):
        raise TypeError("salt must be bytes or bytearray")

    sorted_keys = sorted(hw.keys())
    concat_values = ":".join(hw[k] for k in sorted_keys).encode("utf-8")
    data = concat_values + bytes(salt)
    digest = cast(bytes, hash_sha3(data))
    wipe_bytes(bytearray(data))
    return digest


def _read_file_first_line(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.readline().strip()
    except Exception:  # pragma: no cover - file read error
        return ""


def get_device_fingerprint() -> str:
    """Return fingerprint of this device as a hex string."""
    hw = collect_hw_factors()
    fp = compute_fp(hw, SALT_CONST)
    return fp.hex()


def device_fp_v2() -> bytes:
    """Return SHA3-256 hash of extended hardware factors."""
    factors = [
        _read_file_first_line("/sys/class/dmi/id/product_uuid"),
        _read_file_first_line("/sys/class/dmi/id/board_serial"),
        _read_file_first_line("/sys/class/dmi/id/bios_version"),
        _read_file_first_line("/sys/class/dmi/id/chassis_serial"),
        _read_file_first_line("/sys/class/dmi/id/product_serial"),
        platform.node(),
        format(uuid.getnode(), "x"),
        str(os.cpu_count() or 0),
    ]
    t0 = time.perf_counter_ns()
    for _ in range(1000):
        time.perf_counter_ns()
    jitter = str(time.perf_counter_ns() - t0)
    factors.append(jitter)
    blob = "|".join(factors).encode()
    digest = cast(bytes, hash_sha3(blob))
    wipe_bytes(bytearray(blob))
    return digest
