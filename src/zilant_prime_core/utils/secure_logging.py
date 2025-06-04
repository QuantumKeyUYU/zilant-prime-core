# src/zilant_prime_core/utils/secure_logging.py
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

from __future__ import annotations

import base64
import json
import os
import secrets
import shutil
import subprocess
from typing import Any, Optional, Tuple, Union

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

__all__ = ["SecureLogger", "get_secure_logger"]


class SecureLogger:
    """Логгер с AES-GCM и компактным JSON."""

    def __init__(self, key: Optional[bytes] = None, log_path: str = "secure.log") -> None:
        raw: Optional[bytes] = key
        if raw is None:
            env = os.environ.get("ZILANT_LOG_KEY")
            if env:
                raw = base64.urlsafe_b64decode(env.encode())
            elif shutil.which("tpm2_getrandom"):
                try:
                    raw = subprocess.check_output(["tpm2_getrandom", "32"], timeout=5)
                except Exception:
                    raw = None
        if not isinstance(raw, (bytes, bytearray)) or len(raw) != 32:
            raise ValueError("Log key must be 32 bytes")

        self._aesgcm = AESGCM(raw)
        self.log_path = log_path
        os.makedirs(os.path.dirname(self.log_path) or ".", exist_ok=True)

    def _sanitize(self, msg: str) -> str:
        return "".join(ch for ch in msg.replace("\n", "\\n").replace("\r", "\\r") if 32 <= ord(ch) < 127)

    def log(self, msg: str, level: str = "INFO", **fields: Any) -> None:  # pragma: no cover
        d: dict[str, Any] = {"msg": self._sanitize(msg), "level": level}
        for k, v in fields.items():
            d[k] = v if isinstance(v, (str, int, float, bool)) or v is None else str(v)
        data = json.dumps(d, separators=(",", ":")).encode()
        nonce = secrets.token_bytes(12)
        ct = self._aesgcm.encrypt(nonce, data, None)
        with open(self.log_path, "ab") as f:
            f.write(base64.b64encode(nonce) + b"|" + base64.b64encode(ct) + b"\n")
        if os.path.getsize(self.log_path) == len(base64.b64encode(nonce)) + len(base64.b64encode(ct)) + 2:
            try:
                os.chmod(self.log_path, 0o600)
            except Exception:
                pass

    def read_logs(self) -> list[Union[Tuple[str, str], Tuple[str, str, dict[str, Any]]]]:  # pragma: no cover
        out: list[Union[Tuple[str, str], Tuple[str, str, dict[str, Any]]]] = []
        if not os.path.exists(self.log_path):
            return out
        with open(self.log_path, "rb") as f:
            for line in f:
                try:
                    nonce_b64, ct_b64 = line.rstrip(b"\n").split(b"|")
                    pt = self._aesgcm.decrypt(base64.b64decode(nonce_b64), base64.b64decode(ct_b64), None)
                    payload = json.loads(pt.decode())
                except Exception:
                    continue
                lvl, msg = payload.pop("level", ""), payload.pop("msg", "")
                out.append((lvl, msg))
                if payload:
                    out.append((lvl, msg, payload))
        return out


_default: Optional[SecureLogger] = None


def get_secure_logger(key: Optional[bytes] = None, log_path: str = "secure.log") -> SecureLogger:  # pragma: no cover
    global _default
    if _default is None:
        if key is None and "ZILANT_LOG_KEY" not in os.environ:
            os.environ["ZILANT_LOG_KEY"] = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
        _default = SecureLogger(key=key, log_path=log_path)
    return _default
