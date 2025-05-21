import json
from pathlib import Path
from typing import Any, Dict

from zilant_prime_core.utils.formats import to_b64, from_b64

class MetadataError(Exception):
    """Ошибка сериализации/десериализации метаданных."""

class Metadata:
    def __init__(self, filename: str, size: int, extra: Dict[str, Any] = None):
        self.filename = filename
        self.size = size
        self.extra = extra.copy() if extra else {}

    def to_json_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "filename": self.filename,
            "size": self.size,
        }
        for k, v in self.extra.items():
            if isinstance(v, (bytes, bytearray)):
                d[k] = to_b64(v)
            else:
                d[k] = v
        return d

def new_meta_for_file(path: Path) -> Metadata:
    stat = path.stat()
    return Metadata(filename=path.name, size=stat.st_size)

def serialize_metadata(meta: Any) -> bytes:
    """
    Принимает Metadata или dict → JSON UTF-8 bytes.
    """
    try:
        if isinstance(meta, Metadata):
            d = meta.to_json_dict()
        elif isinstance(meta, dict):
            d = meta
        else:
            raise MetadataError(f"Unsupported metadata type: {type(meta)}")
        return json.dumps(d).encode("utf-8")
    except (TypeError, ValueError) as e:
        raise MetadataError(str(e))

def deserialize_metadata(b: bytes) -> Dict[str, Any]:
    """
    Читает JSON UTF-8 bytes → dict.
    """
    try:
        return json.loads(b.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as e:
        raise MetadataError(str(e))
