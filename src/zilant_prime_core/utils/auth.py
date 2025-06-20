from argon2 import PasswordHasher
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
        ph = PasswordHasher()
        digest = ph.hash(f"{username}:{password}")
        (out_dir / f"{username}.cred").write_text(digest)

    def login(self, username: str, password: str, cred_dir: Path) -> bool:
        """Проверяет пароль по OPAQUE-данным."""
        stored = (cred_dir / f"{username}.cred").read_text()
        ph = PasswordHasher()
        try:
            ph.verify(stored, f"{username}:{password}")
            return True
        except Exception:
            return False
