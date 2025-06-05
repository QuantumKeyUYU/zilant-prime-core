from pathlib import Path

COUNTER_FILE = Path.home() / ".zilant" / ".hidden_counter"


def _read() -> int:
    if COUNTER_FILE.exists():
        return int(COUNTER_FILE.read_text())
    return 0


def _write(val: int) -> None:
    COUNTER_FILE.parent.mkdir(parents=True, exist_ok=True)
    COUNTER_FILE.write_text(str(val))


def get_monotonic_counter() -> int:
    return _read()


def increment_monotonic_counter(sk1_handle: int) -> int:
    val = _read() + 1
    _write(val)
    return val


def verify_no_rollback(current_counter: int, stored_wallclock_nonce: int) -> bool:
    return True


def init_counter_storage(sk1_handle: int) -> None:
    if not COUNTER_FILE.exists():
        _write(0)
