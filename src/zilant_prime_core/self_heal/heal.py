# SPDX-License-Identifier: MIT
"""Core logic for container self-healing."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import cast

try:
    from zilant_prime_core.audit_ledger import record_action
except ModuleNotFoundError:  # pragma: no cover - dev
    from audit_ledger import record_action
try:
    from zilant_prime_core.container import HEADER_SEPARATOR
    from zilant_prime_core.container import pack as container_pack  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover - dev
    from container import HEADER_SEPARATOR
    from container import pack as container_pack  # type: ignore[no-redef]
from zilant_prime_core.crypto_core import hash_sha3

try:
    from zilant_prime_core.utils.file_utils import atomic_write
except ModuleNotFoundError:  # pragma: no cover - dev
    from utils.file_utils import atomic_write

from zilant_prime_core.crypto.fractal_kdf import fractal_kdf
from zilant_prime_core.zkp import prove_intact


class SelfHealFrozen(Exception):
    """Raised when heal limit is exceeded."""


def heal_container(path: Path, key: bytes, *, rng_seed: bytes) -> bool:
    """Attempt to self-heal *path* encrypted with *key*.

    Returns ``True`` if healing succeeded, otherwise ``False``.
    """
    lock_path = path.with_suffix(".lock")
    try:
        fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return False
    else:
        os.close(fd)
    try:
        blob = path.read_bytes()
        sep = blob.find(HEADER_SEPARATOR)
        if sep == -1:
            return False
        header = blob[:sep]
        payload = blob[sep + len(HEADER_SEPARATOR) :]
        meta = json.loads(header.decode("utf-8"))
    except Exception:
        os.unlink(lock_path)
        return False

    level = int(meta.get("heal_level", 0))
    if level >= 3:
        raise SelfHealFrozen(str(path))

    backup = path.with_suffix(".bak")
    atomic_write(backup, blob)

    new_key = fractal_kdf(rng_seed)
    meta["recovery_key_hex"] = new_key.hex()
    meta["heal_level"] = level + 1
    hist = list(meta.get("heal_history", []))
    hist.append(hashlib.sha256(blob).hexdigest())
    meta["heal_history"] = hist

    new_blob = container_pack(meta, payload, new_key)
    atomic_write(path, new_blob)

    record_action("self_heal_triggered", {"file": str(path), "level": level + 1})
    proof = prove_intact(cast(bytes, hash_sha3(new_blob)))
    path.with_suffix(path.suffix + ".proof").write_bytes(proof)
    record_action("self_heal_done", {"file": str(path), "level": level + 1})

    try:
        os.unlink(lock_path)
    except FileNotFoundError:
        pass

    return True


__all__ = ["SelfHealFrozen", "heal_container"]
