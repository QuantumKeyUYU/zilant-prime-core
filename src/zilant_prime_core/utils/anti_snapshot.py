import os
import time
from pathlib import Path

LOCK_FILE = (
    Path("/var/lock/zilant_pseudohsm.lock")
    if os.name != "nt"
    else Path(os.path.expanduser("~\\AppData\\Local\\zilant_pseudohsm.lock"))
)


def acquire_snapshot_lock(sk1_handle: int) -> None:
    data = f"{os.getpid()} {int(time.time())}\n".encode()
    with open(LOCK_FILE, "wb") as f:
        f.write(data)


def check_snapshot_freshness(sk1_handle: int) -> None:
    if not LOCK_FILE.exists():
        return
    ts = int(LOCK_FILE.read_text().split()[1])
    if time.time() - ts > 300:
        raise RuntimeError("stale lock")
