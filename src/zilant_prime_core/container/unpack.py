from pathlib import Path

from zilant_prime_core.utils.constants import DEFAULT_SALT_LENGTH, DEFAULT_NONCE_LENGTH
from zilant_prime_core.crypto.kdf import derive_key
from zilant_prime_core.crypto.aead import decrypt_aead, AEADInvalidTagError
from zilant_prime_core.container.metadata import deserialize_metadata, MetadataError


class UnpackError(Exception):
    """Ошибка при распаковке контейнера."""

    pass


def unpack(container: bytes | Path, output_dir: Path | str, password: str) -> Path:
    # 0) raw bytes
    raw = Path(container).read_bytes() if isinstance(container, Path) else container
    offset = 0

    # 1) 길 meta length (4 bytes big-endian)
    if len(raw) < offset + 4:
        raise UnpackError("Контейнер слишком мал для метаданных.")
    meta_len = int.from_bytes(raw[offset : offset + 4], "big")
    offset += 4

    # 2) meta blob
    if len(raw) < offset + meta_len:
        raise UnpackError("Неполные метаданные.")
    meta_blob = raw[offset : offset + meta_len]
    offset += meta_len
    try:
        meta = deserialize_metadata(meta_blob)
    except MetadataError as e:
        raise UnpackError(f"Не удалось разобрать метаданные: {e}")

    # 3) salt
    if len(raw) < offset + DEFAULT_SALT_LENGTH:
        raise UnpackError("Неправильный формат контейнера (salt).")
    salt = raw[offset : offset + DEFAULT_SALT_LENGTH]
    offset += DEFAULT_SALT_LENGTH

    # 4) nonce
    if len(raw) < offset + DEFAULT_NONCE_LENGTH:
        raise UnpackError("Неправильный формат контейнера (nonce).")
    nonce = raw[offset : offset + DEFAULT_NONCE_LENGTH]
    offset += DEFAULT_NONCE_LENGTH

    # 5) ciphertext||tag (остаток)
    ct_and_tag = raw[offset:]
    if len(ct_and_tag) < 16:
        raise UnpackError("Ciphertext слишком короткий для включения тега.")

    # 6) derive key + decrypt
    key = derive_key(password.encode("utf-8"), salt)
    try:
        payload = decrypt_aead(key, nonce, ct_and_tag, aad=meta_blob)
    except AEADInvalidTagError:
        raise UnpackError("Неверная метка аутентификации.")
    except Exception as e:
        raise UnpackError(f"Ошибка дешифрования: {e}")

    # 7) write file
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / meta["filename"]
    if out_file.exists():
        raise FileExistsError(f"{out_file} уже существует.")
    out_file.write_bytes(payload)
    return out_file
