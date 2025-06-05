# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

import os
import struct
import sys
import time

import click
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from zilant_prime_core.utils.anti_snapshot import (
    acquire_snapshot_lock,
    check_snapshot_freshness,
)
from zilant_prime_core.utils.counter import (
    get_monotonic_counter,
    increment_monotonic_counter,
    init_counter_storage,
    set_sk1_handle,
)
from zilant_prime_core.utils.crypto_wrapper import (
    derive_sk0_from_fp,
    derive_sk1,
    get_sk_bytes,
    release_sk,
)
from zilant_prime_core.utils.device_fp import get_device_fp
from zilant_prime_core.utils.hardening import apply_runtime_hardening
from zilant_prime_core.utils.logging import log_event, self_destruct_all
from zilant_prime_core.utils.shard_secret import (
    generate_shard,
    load_shard,
)

global_sk1_handle: int | None = None

COSIGN_PUBKEY = bytes.fromhex("d9f8e7a6b5c4d3e2f1d9f8e7a6b5c4d3e2f1d9f8e7a6b5c4d3e2f1e2d3c4b5a6d7e8")


def verify_cosign_signature(binary_path: str) -> None:
    """Проверяет Ed25519-подпись файла."""
    with open(binary_path, "rb") as f:
        data = f.read()
    if len(data) < 64:
        sys.exit(137)
    sig = data[-64:]
    data_wo_sig = data[:-64]
    try:
        pub = Ed25519PublicKey.from_public_bytes(COSIGN_PUBKEY)
        pub.verify(sig, data_wo_sig)
    except InvalidSignature:
        sys.exit(137)


@click.group()
def cli() -> None:
    if not os.getenv("DISABLE_COSIGN_CHECK"):
        verify_cosign_signature(__file__)
    if not os.getenv("DISABLE_HARDENING"):
        apply_runtime_hardening()

    device_fp = get_device_fp()
    sk0_handle = derive_sk0_from_fp(device_fp)
    pwd = click.prompt("Enter encryption password", hide_input=True)
    sk1_handle = derive_sk1(sk0_handle, pwd.encode("utf-8"))

    global global_sk1_handle
    global_sk1_handle = sk1_handle
    set_sk1_handle(sk1_handle)

    init_counter_storage(sk1_handle)
    check_snapshot_freshness(sk1_handle)
    acquire_snapshot_lock(sk1_handle)
    release_sk(sk0_handle)


@cli.command()
@click.argument("output_shard", type=click.Path())
def enrol(output_shard: str) -> None:
    assert global_sk1_handle is not None
    shard_blob = generate_shard(global_sk1_handle)
    with open(output_shard, "wb") as f:
        f.write(shard_blob)
    click.echo(f"Shard создан: {output_shard}. Сделайте backup и сохраните recovery-phrase.")


@cli.command()
@click.argument("input_shard", type=click.Path(exists=True))
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_container", type=click.Path())
def pack(input_shard: str, input_file: str, output_container: str) -> None:
    assert global_sk1_handle is not None
    with open(input_shard, "rb") as f:
        encrypted_shard = f.read()
    try:
        shard = load_shard(global_sk1_handle, encrypted_shard)
    except Exception as e:
        click.echo("Не удалось загрузить shard: " + str(e))
        sys.exit(1)

    with open(input_file, "rb") as f_in:
        plaintext = f_in.read()

    nonce = os.urandom(12)
    device_fp = get_device_fp()
    new_counter = increment_monotonic_counter(global_sk1_handle)
    sk1 = get_sk_bytes(global_sk1_handle)
    data_for_seed = nonce + device_fp + shard.shard_id.bytes + struct.pack(">Q", new_counter)
    import hashlib
    import hmac as _hmac_module

    seed = _hmac_module.new(sk1, data_for_seed, hashlib.sha256).digest()

    from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

    aead = ChaCha20Poly1305(seed)
    ciphertext = aead.encrypt(nonce, plaintext, None)

    version = 1
    header = struct.pack(">I", version) + nonce + seed + struct.pack(">Q", new_counter)
    container_blob = header + ciphertext
    with open(output_container, "wb") as f_out:
        f_out.write(container_blob)

    log_event("PACK_SUCCESS", {"container": output_container, "counter": new_counter}, global_sk1_handle)
    click.echo(f"Packed into {output_container}")


@cli.command()
@click.argument("input_shard", type=click.Path(exists=True))
@click.argument("input_container", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
def unpack(input_shard: str, input_container: str, output_file: str) -> None:
    assert global_sk1_handle is not None
    with open(input_shard, "rb") as f:
        encrypted_shard = f.read()
    try:
        shard = load_shard(global_sk1_handle, encrypted_shard)
    except Exception as e:
        click.echo("Не удалось загрузить shard: " + str(e))
        sys.exit(1)

    with open(input_container, "rb") as f:
        blob = f.read()
    _ = struct.unpack(">I", blob[:4])[0]
    nonce = blob[4:16]
    seed = blob[16:48]
    stored_counter = struct.unpack(">Q", blob[48:56])[0]
    ciphertext = blob[56:]

    current_counter = get_monotonic_counter()
    if stored_counter != shard.usage_counter:
        self_destruct_all()
    now_nonce = (int(time.time()) + 299) // 300
    if now_nonce < shard.wallclock_nonce:
        self_destruct_all()

    sk1 = get_sk_bytes(global_sk1_handle)
    device_fp = get_device_fp()
    data_for_seed = nonce + device_fp + shard.shard_id.bytes + struct.pack(">Q", stored_counter)
    import hashlib
    import hmac as _hmac_module

    expected_seed = _hmac_module.new(sk1, data_for_seed, hashlib.sha256).digest()
    if expected_seed != seed:
        self_destruct_all()

    from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

    try:
        plaintext = ChaCha20Poly1305(seed).decrypt(nonce, ciphertext, None)
    except Exception:
        self_destruct_all()
        sys.exit(1)

    with open(output_file, "wb") as f_out:
        f_out.write(plaintext)

    log_event("UNPACK_SUCCESS", {"container": input_container, "counter": current_counter}, global_sk1_handle)
    click.echo(f"Unpacked into {output_file}")


if __name__ == "__main__":
    cli()

main = cli
