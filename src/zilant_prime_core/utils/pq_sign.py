from pathlib import Path
from typing import cast

try:
    import oqs  # PQ-Crypto (Dilithium)

    if hasattr(oqs, "Signature"):
        _HAS_OQS = True
    else:  # pragma: no cover - wrong oqs package
        raise ImportError
except ImportError:  # pragma: no cover - optional dependency
    from nacl import signing  # Fallback Ed25519

    _HAS_OQS = False


class PQSign:
    """Unified API for post-quantum signatures (Dilithium-3 ➜ fallback Ed25519)."""

    def __init__(self) -> None:
        if _HAS_OQS:
            self.alg = "Dilithium3"
            self.sig = oqs.Signature(self.alg)
        else:
            self.alg = "Ed25519"
            self.sk = signing.SigningKey.generate()

    # ---------- keygen ----------
    def keygen(self, priv_path: Path, pub_path: Path) -> None:
        if _HAS_OQS:
            pk, sk = self.sig.generate_keypair()
            priv_path.write_bytes(sk)
            pub_path.write_bytes(pk)
        else:
            priv_path.write_bytes(self.sk.encode())
            pub_path.write_bytes(self.sk.verify_key.encode())

    # ---------- sign ------------
    def sign(self, message: bytes, priv_path: Path) -> bytes:
        if _HAS_OQS:
            sk_bytes = priv_path.read_bytes()
            return cast(bytes, self.sig.sign(message, sk_bytes))
        else:
            sk_obj = signing.SigningKey(priv_path.read_bytes())
            return cast(bytes, sk_obj.sign(message).signature)

    # ---------- verify ----------
    def verify(self, message: bytes, signature: bytes, pub_path: Path) -> bool:
        if _HAS_OQS:
            pk_bytes = pub_path.read_bytes()
            return cast(bool, self.sig.verify(message, signature, pk_bytes))
        else:
            vk = signing.VerifyKey(pub_path.read_bytes())
            try:
                vk.verify(message, signature)
                return True
            except Exception:
                return False
