import base64


def to_hex(data: bytes) -> str:
    return data.hex()


def from_hex(s: str) -> bytes:
    try:
        return bytes.fromhex(s)
    except ValueError as e:
        raise ValueError(f"Invalid hex string: {e}")


def to_b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def from_b64(s: str) -> bytes:
    try:
        return base64.b64decode(s, validate=True)
    except (base64.binascii.Error, ValueError) as e:
        raise ValueError(f"Invalid base64 string: {e}")
