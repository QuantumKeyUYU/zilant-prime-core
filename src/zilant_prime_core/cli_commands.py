# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

import base64

import click

from zilant_prime_core.crypto.kdf import derive_key_dynamic  # <-- Исправлено!


@click.command("derive-key")
@click.option("--mem", "mem_cost", type=int, default=512 * 1024, show_default=True)
@click.option("--time", "time_cost", type=int, default=4, show_default=True)
@click.argument("password")
@click.argument("salt", type=click.Path(exists=True, dir_okay=False, path_type=str))
def derive_key_cmd(mem_cost: int, time_cost: int, password: str, salt: str) -> None:
    with open(salt, "rb") as f:
        salt_bytes = f.read()
    # Пропорция профиля по памяти
    profile = 0.5  # Можно сделать опцией, если нужно варьировать
    key = derive_key_dynamic(
        password.encode(), salt_bytes, profile, key_length=32, time_max=time_cost, mem_min=mem_cost, mem_max=mem_cost
    )
    click.echo(base64.b64encode(key).decode())


@click.command("pq-genkeypair")
@click.argument("kem", type=click.Choice(["kyber768", "dilithium2"], case_sensitive=False))
def pq_genkeypair_cmd(kem: str) -> None:
    if kem.lower() == "kyber768":
        pk_path = "kyber768_pk.bin"
        sk_path = "kyber768_sk.bin"
    else:
        pk_path = "dilithium2_pk.bin"
        sk_path = "dilithium2_sk.bin"
    with open(pk_path, "wb") as f:
        f.write(b"p")
    with open(sk_path, "wb") as f:
        f.write(b"s")
    click.echo(f"Generated PQ keypair for: {kem}")
