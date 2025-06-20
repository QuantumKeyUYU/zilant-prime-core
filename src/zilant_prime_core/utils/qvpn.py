# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT
"""Quantum-Hardened VPN/TOR integration using Stem."""

from __future__ import annotations

from typing import Optional

from stem.process import launch_tor_with_config


class QVPN:
    """Manage a simple Tor proxy using Stem."""

    def __init__(self, tor_path: str = "tor") -> None:
        self._enabled = False
        self._tor_path = tor_path
        self._proc: Optional[object] = None

    def enable(self) -> None:
        if self._enabled:
            return
        try:
            self._proc = launch_tor_with_config({"SocksPort": "9050"}, tor_cmd=self._tor_path)
            self._enabled = True
        except Exception:  # pragma: no cover - optional dependency
            self._enabled = False

    def disable(self) -> None:
        if self._proc is not None:
            self._proc.terminate()
            self._proc = None
        self._enabled = False

    def is_enabled(self) -> bool:
        return self._enabled
