# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
from __future__ import annotations

import base64
import click
import sys
from pathlib import Path
from typing import Final

from zilant_prime_core.crypto.kdf import derive_key_dynamic
from zilant_prime_core.crypto.password_hash import hash_password, verify_password

__all__: Final = [
    "derive_key_cmd",
    "pw_hash_cmd",
    "pw_verify_cmd",
    "pq_genkeypair_cmd",
]


# ─────────────────── derive‑key ───────────────────
@click.command("derive-key")
@click.option("--mem", "mem_cost", type=int, default=512 * 1024, show_default=True)
@click.option("--time", "time_cost", type=int, default=4, show_default=True)
@click.argument("password")
@click.argument("salt", type=click.Path(exists=True, dir_okay=False, path_type=str))
def derive_key_cmd(mem_cost: int, time_cost: int, password: str, salt: str) -> None:
    """Generate a 32‑byte Argon2id key and print it as Base64."""
    key = derive_key_dynamic(
        password=password.encode(),
        salt=Path(salt).read_bytes(),
        profile=0.5,
        key_length=32,
        time_max=time_cost,
        mem_min=mem_cost,
        mem_max=mem_cost,
    )
    click.echo(base64.b64encode(key).decode())


# ─────────────────── pw‑hash ───────────────────
@click.command("pw-hash")
@click.argument("password")
def pw_hash_cmd(password: str) -> None:  # pragma: no cover
    """Print Argon2id hash of *password*."""
    click.echo(hash_password(password))  # pragma: no cover


# ─────────────────── pw‑verify ───────────────────
@click.command("pw-verify")
@click.argument("password")
@click.argument("hash")
def pw_verify_cmd(password: str, hash: str) -> None:  # pragma: no cover
    """Exit 0 if *password* matches *hash*, else exit 1."""
    ok = verify_password(hash, password)  # pragma: no cover
    click.echo("ok" if ok else "fail", err=not ok)  # pragma: no cover
    if not ok:  # pragma: no cover
        sys.exit(1)  # pragma: no cover


# ─────────────────── pq-genkeypair (stub) ───────────────────
@click.command("pq-genkeypair")
@click.argument("kem", type=click.Choice(["kyber768", "dilithium2"], case_sensitive=False))
def pq_genkeypair_cmd(kem: str) -> None:  # pragma: no cover
    """Temporary stub that writes dummy PQ keypair files."""
    pk_path = Path(f"{kem.lower()}_pk.bin")
    sk_path = Path(f"{kem.lower()}_sk.bin")
    pk_path.write_bytes(b"p")  # pragma: no cover
    sk_path.write_bytes(b"s")  # pragma: no cover
    click.echo(f"Generated PQ keypair: {pk_path}, {sk_path}")  # pragma: no cover
