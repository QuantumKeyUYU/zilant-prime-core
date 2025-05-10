# src/zil.py

import hashlib
import json
import struct
from pathlib import Path

from aead import decrypt, encrypt

MAGIC = b"ZIL1"
VERSION = 1


class ZilFormatError(Exception):
    pass


class SelfDestructError(Exception):
    pass


class InvalidError(Exception):
    """Uniform error for any non‐fatal authentication failure."""

    pass


def pack_zil(
    payload: bytes,
    formula,
    lam: float,
    steps: int,
    key: bytes,
    salt: bytes,
    nonce: bytes,
    metadata: dict,
    max_tries: int = 3,
    one_time: bool = True,
) -> bytes:
    flags = 0x01 if one_time else 0x00

    # Phase-VDF (или stub)
    try:
        from elc_vdf import generate_phase_vdf

        cps = generate_phase_vdf(formula, steps, lam)
        state, _ = cps[-1]
        vdf_proof = state.tobytes()
        real_steps, real_lam = steps, lam
    except Exception:
        vdf_proof = b""
        real_steps, real_lam = 0, 0.0

    # AEAD шифрование с AAD = vdf_proof
    _, ciphertext = encrypt(key, payload, vdf_proof, nonce)

    # JSON-metadata
    meta_json = json.dumps(metadata).encode("utf-8")

    # Phase Fingerprint = SHA256(vdf_proof ∥ key)
    fingerprint = hashlib.sha256(vdf_proof + key).digest()

    return b"".join(
        [
            MAGIC,
            struct.pack("!B", VERSION),
            struct.pack("!B", flags),
            struct.pack("!H", len(salt)),
            salt,
            struct.pack("!H", len(nonce)),
            nonce,
            struct.pack("!B", max_tries),
            struct.pack("!B", 1 if one_time else 0),
            struct.pack("!I", real_steps),
            struct.pack("!d", real_lam),
            struct.pack("!I", len(vdf_proof)),
            vdf_proof,
            struct.pack("!I", len(ciphertext)),
            ciphertext,
            struct.pack("!I", len(fingerprint)),
            fingerprint,
            struct.pack("!I", len(meta_json)),
            meta_json,
        ]
    )


def unpack_zil(data: bytes, formula, key: bytes, out_dir: str = ".") -> bytes:
    """
    In-memory распаковка .zil → payload.
    • при превышении max_tries → SelfDestructError
    • любой fingerprint/decrypt/marker-фатал → InvalidError
    Не трогает файл на диске.
    """
    # сначала пробуем обнаружить состояние самоуничтожения
    buf = memoryview(data)
    off = 0

    if buf[off : off + 4] != MAGIC:
        raise ZilFormatError("Invalid magic")
    off += 4
    off += 1  # версия
    flags = buf[off]
    off += 1
    one_time = bool(flags & 0x01)

    # salt
    salt_len = struct.unpack_from("!H", buf, off)[0]
    off += 2 + salt_len

    # nonce
    nonce_len = struct.unpack_from("!H", buf, off)[0]
    off += 2
    nonce = bytes(buf[off : off + nonce_len])
    off += nonce_len

    # max_tries и флаг one_time
    max_tries = buf[off]
    off += 1
    off += 1

    # пропускаем steps+lam
    off += 4 + 8

    # proof
    vdf_len = struct.unpack_from("!I", buf, off)[0]
    off += 4
    vdf_proof = bytes(buf[off : off + vdf_len])
    off += vdf_len

    # ciphertext
    ct_len = struct.unpack_from("!I", buf, off)[0]
    off += 4
    ciphertext = bytes(buf[off : off + ct_len])
    off += ct_len

    # fingerprint
    fp_len = struct.unpack_from("!I", buf, off)[0]
    off += 4
    stored_fp = bytes(buf[off : off + fp_len])
    off += fp_len

    # metadata
    meta_len = struct.unpack_from("!I", buf, off)[0]
    off += 4
    metadata = json.loads(bytes(buf[off : off + meta_len]))
    off += meta_len
    tries = metadata.get("tries", 0)

    # проверяем самоуничтожение
    if not one_time and tries + 1 >= max_tries:
        raise SelfDestructError("Max tries exceeded")

    if one_time:
        marker = Path(out_dir) / f".zil_once_{hash(data)}"
        if marker.exists():
            raise SelfDestructError("Max tries exceeded")

    # аутентификация и расшифровка
    try:
        # fingerprint
        expected_fp = hashlib.sha256(vdf_proof + key).digest()
        if stored_fp != expected_fp:
            raise Exception()
        # decrypt
        payload = decrypt(key, nonce, ciphertext, vdf_proof)
    except SelfDestructError:
        # не должно попасть сюда
        raise
    except Exception:
        raise InvalidError("Invalid")

    # отмечаем one_time
    if one_time:
        marker.write_bytes(b"")

    return payload


def pack_zil_file(
    path: str,
    payload: bytes,
    formula,
    lam: float,
    steps: int,
    key: bytes,
    salt: bytes,
    nonce: bytes,
    metadata: dict,
    max_tries: int = 3,
    one_time: bool = True,
) -> None:
    Path(path).write_bytes(
        pack_zil(
            payload,
            formula,
            lam,
            steps,
            key,
            salt,
            nonce,
            metadata,
            max_tries,
            one_time,
        )
    )


def unpack_zil_file(path: str, formula, key: bytes, out_dir: str = ".") -> bytes:
    """
    File-based распаковка .zil.
    • любая auth/fp ошибка → tries+=1, inline JSON,
       если после инкремента ≥ max_tries или one_time=True → удалить + SelfDestructError
       до этого — InvalidError
    • успешная расшифровка → tries+=1 inline (если multi_try) или сразу удаление
    """
    file = Path(path)
    raw = file.read_bytes()
    buf = memoryview(raw)
    off = 0

    # header
    if buf[off : off + 4] != MAGIC:
        raise InvalidError("Invalid")
    off += 4
    off += 1
    flags = buf[off]
    off += 1
    one_time = bool(flags & 0x01)

    off += 2
    salt_len = struct.unpack_from("!H", buf, off - 2)[0]
    off += salt_len
    off += 2
    nonce_len = struct.unpack_from("!H", buf, off - 2)[0]
    nonce = bytes(buf[off : off + nonce_len])
    off += nonce_len

    max_tries = buf[off]
    off += 1
    off += 1

    off += 4 + 8  # steps+lam

    vdf_len = struct.unpack_from("!I", buf, off)[0]
    off += 4
    vdf_proof = bytes(buf[off : off + vdf_len])
    off += vdf_len

    ct_len = struct.unpack_from("!I", buf, off)[0]
    off += 4
    ciphertext = bytes(buf[off : off + ct_len])
    off += ct_len

    fp_len = struct.unpack_from("!I", buf, off)[0]
    off += 4
    stored_fp = bytes(buf[off : off + fp_len])
    off += fp_len

    meta_off = off
    meta_len = struct.unpack_from("!I", buf, off)[0]
    off += 4
    meta_json = bytes(buf[off : off + meta_len])
    off += meta_len
    metadata = json.loads(meta_json)
    tries = metadata.get("tries", 0)

    def _rewrite_meta(new_meta):
        b = json.dumps(new_meta).encode("utf-8")
        return (
            raw[:meta_off]
            + struct.pack("!I", len(b))
            + b
            + raw[meta_off + 4 + meta_len :]
        )

    # аутентификация / decrypt
    try:
        # fingerprint
        if stored_fp != hashlib.sha256(vdf_proof + key).digest():
            raise Exception()
        payload = decrypt(key, nonce, ciphertext, vdf_proof)
    except Exception:
        # неудача → tries+=1
        metadata["tries"] = tries + 1
        file.write_bytes(_rewrite_meta(metadata))
        # удаляем при переполнении или one_time
        if one_time or metadata["tries"] >= max_tries:
            file.unlink(missing_ok=True)
            raise SelfDestructError("Max tries exceeded")
        # иначе uniform feedback
        raise InvalidError("Invalid")

    # успех
    if one_time or tries + 1 >= max_tries:
        file.unlink(missing_ok=True)
    else:
        metadata["tries"] = tries + 1
        file.write_bytes(_rewrite_meta(metadata))

    return payload
