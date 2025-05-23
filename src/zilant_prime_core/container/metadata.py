"""
(Де)сериализация простейших метаданных об архиве.

Используется во внутреннем формате `.zil`.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping, MutableMapping

__all__ = [
    "Metadata",
    "MetadataError",
    "new_meta_for_file",
    "serialize_metadata",
    "deserialize_metadata",
]


class MetadataError(RuntimeError):
    """Некорректный JSON / отсутствующие поля и т.д."""


@dataclass(slots=True, frozen=True)
class Metadata:
    name: str
    size: int
    sha256: str
    extra: Mapping[str, Any] | None = None


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def new_meta_for_file(path: Path, *, extra: Mapping[str, Any] | None = None) -> Metadata:
    return Metadata(name=path.name, size=path.stat().st_size, sha256=_sha256(path), extra=extra)


# ────────────────────────────── JSON helpers ────────────────────────────── #


def serialize_metadata(meta: Metadata) -> str:
    return json.dumps(asdict(meta), separators=(",", ":"))


def deserialize_metadata(data: str) -> Metadata:
    try:
        obj: MutableMapping[str, Any] = json.loads(data)
        return Metadata(**obj)  # type: ignore[arg-type]
    except Exception as exc:  # pragma: no cover
        raise MetadataError("invalid metadata JSON") from exc
