import json
import struct

class SelfDestructError(Exception):
    """Подбрасывается при превышении числа попыток."""

def pack_zill(
    payload: bytes,
    formula,
    lam,
    steps,
    key,
    salt,
    nonce,
    metadata: dict,
    max_tries: int,
    one_time: bool,
) -> bytes:
    # Встраиваем параметры попыток в метаданные
    meta = metadata.copy()
    meta["max_tries"] = max_tries
    meta["one_time"] = one_time
    meta_bytes = json.dumps(meta).encode("utf-8")
    return struct.pack(">I", len(meta_bytes)) + meta_bytes + payload

def unpack_zil(data: bytes, formula, key, out_dir: str):
    offset = 0
    total = len(data)
    # читаем длину JSON-метаданных
    meta_len = struct.unpack_from(">I", data, offset)[0]
    offset += 4
    meta_bytes = data[offset:offset + meta_len]
    offset += meta_len
    metadata = json.loads(meta_bytes.decode("utf-8"))
    payload = data[offset:total]

    tries = metadata.get("tries", 0)
    max_tries = metadata.get("max_tries", 0)
    one_time = metadata.get("one_time", False)

    # логика «самоуничтожения»
    if one_time and tries > 0:
        raise SelfDestructError("One-time container can’t be reused.")
    if not one_time and tries >= (max_tries - 1):
        raise SelfDestructError("Max tries exceeded.")

    return payload
