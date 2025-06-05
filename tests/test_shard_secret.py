from zilant_prime_core.utils.counter import init_counter_storage, set_sk1_handle
from zilant_prime_core.utils.crypto_wrapper import derive_sk0_from_fp, derive_sk1, release_sk
from zilant_prime_core.utils.device_fp import get_device_fp
from zilant_prime_core.utils.shard_secret import generate_shard, load_shard


def test_shard_generate_load(tmp_path):
    fp = get_device_fp()
    sk0 = derive_sk0_from_fp(fp)
    sk1 = derive_sk1(sk0, b"pwd")
    set_sk1_handle(sk1)
    init_counter_storage(sk1)
    blob = generate_shard(sk1)
    shard = load_shard(sk1, blob)
    assert shard.shard_key
    release_sk(sk0)
    release_sk(sk1)
