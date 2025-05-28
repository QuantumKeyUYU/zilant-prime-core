# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

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
    """
    Упаковывает данные вместе с JSON-метаданными, в которые
    встраивается максимальное число попыток и флаг one_time.
    """
    meta = metadata.copy()
    meta["max_tries"] = max_tries
    meta["one_time"] = one_time
    meta_bytes = json.dumps(meta).encode("utf-8")
    # 4 байта длины + JSON + собственно payload
    return struct.pack(">I", len(meta_bytes)) + meta_bytes + payload


def unpack_zil(data: bytes, formula, key, out_dir: str) -> bytes:
    """
    Распаковывает контейнер, проверяет число попыток и
    при необходимости выбрасывает SelfDestructError.
    Возвращает исходный payload.
    """
    offset = 0
    total = len(data)
    # 1) читаем длину JSON-метаданных
    meta_len = struct.unpack_from(">I", data, offset)[0]
    offset += 4

    # 2) вычленяем и парсим метаданные
    meta_bytes = data[offset : offset + meta_len]
    offset += meta_len
    metadata = json.loads(meta_bytes.decode("utf-8"))

    # 3) собственно полезные данные
    payload = data[offset:total]

    # 4) логика «самоуничтожения»
    tries = metadata.get("tries", 0)
    max_tries = metadata.get("max_tries", 0)
    one_time = metadata.get("one_time", False)

    if one_time and tries > 0:
        raise SelfDestructError("One-time container can’t be reused.")
    if not one_time and tries >= (max_tries - 1):
        raise SelfDestructError("Max tries exceeded.")

    return payload
