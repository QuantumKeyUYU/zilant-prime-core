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
        cred = f"{username}:{password}".encode()
        (out_dir / f"{username}.cred").write_bytes(cred)

    def login(self, username: str, password: str, cred_dir: Path) -> bool:
        """Проверяет пароль по OPAQUE-данным."""
        data = (cred_dir / f"{username}.cred").read_bytes()
        stored = data.decode().split(":", 1)
        return username == stored[0] and password == stored[1]
