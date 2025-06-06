__all__ = ["wipe_bytes"]

def wipe_bytes(buf: bytearray) -> None:
    """Overwrite the given bytearray with zeros."""
    if not isinstance(buf, bytearray):
        raise TypeError("buf must be bytearray")
    for i in range(len(buf)):
        buf[i] = 0
