from argon2 import PasswordHasher
from pathlib import Path

try:
    import oqs  # type: ignore

    _HAS_OQS = True  # pragma: no cover – depends on external lib
except ImportError:
    _HAS_OQS = False


class OpaqueAuth:
    """OPAQUE-style registration / login (stub)."""

    def __init__(self) -> None:
        if not _HAS_OQS:
            raise RuntimeError("OPAQUE support requires oqs library")
        self.server = oqs.KeyEncapsulation("Kyber512")  # placeholder

    # ------------------------------------------------------------------
    def register(self, username: str, password: str, out_dir: Path) -> None:
        """Save hashed creds for *username* in *out_dir*."""
        out_dir.mkdir(parents=True, exist_ok=True)
        ph = PasswordHasher()
        digest = ph.hash(f"{username}:{password}")
        (out_dir / f"{username}.cred").write_text(digest)

    # ------------------------------------------------------------------
    def login(self, username: str, password: str, cred_dir: Path) -> bool:
        """Validate *password* against stored OPAQUE creds."""
        stored = (cred_dir / f"{username}.cred").read_text()
        ph = PasswordHasher()
        try:
            ph.verify(stored, f"{username}:{password}")
            return True
        except Exception:
            return False
