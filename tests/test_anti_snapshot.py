import os

from zilant_prime_core.utils.anti_snapshot import LOCK_PATH, acquire_snapshot_lock, check_snapshot_freshness
from zilant_prime_core.utils.counter import init_counter_storage, set_sk1_handle
from zilant_prime_core.utils.crypto_wrapper import derive_sk0_from_fp, derive_sk1
from zilant_prime_core.utils.device_fp import get_device_fp


def test_snapshot_lock(tmp_path):
    fp = get_device_fp()
    sk0 = derive_sk0_from_fp(fp)
    sk1 = derive_sk1(sk0, b"pwd")
    set_sk1_handle(sk1)
    init_counter_storage(sk1)
    acquire_snapshot_lock(sk1)
    assert os.path.exists(LOCK_PATH)
    check_snapshot_freshness(sk1)
