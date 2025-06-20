import hashlib
from pathlib import Path

try:
    import oqs

    _HAS_OQS = True
except ImportError:
    _HAS_OQS = False


class OpaqueAuth:
    """OPAQUE-based registration and login (stub)."""

    def __init__(self) -> None:
        if not _HAS_OQS:
            raise RuntimeError("OPAQUE support requires oqs library")
        self.server = oqs.KeyEncapsulation("Kyber512")  # placeholder

    def register(self, username: str, password: str, out_dir: Path) -> None:
        """Генерирует OPAQUE-регистр и сохраняет данные."""
        out_dir.mkdir(exist_ok=True, parents=True)
        # TODO: реальная логика OPAQUE
        # храним только SHA-256 хеш учётных данных, а не сам пароль
        raw = f"{username}:{password}".encode()
        digest = hashlib.sha256(raw).digest()
        (out_dir / f"{username}.cred").write_bytes(digest)

    def login(self, username: str, password: str, cred_dir: Path) -> bool:
        """Проверяет пароль по OPAQUE-данным."""
        data = (cred_dir / f"{username}.cred").read_bytes()
        raw = f"{username}:{password}".encode()
        digest = hashlib.sha256(raw).digest()
        return data == digest
