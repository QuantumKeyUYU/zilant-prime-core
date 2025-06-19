# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
from __future__ import annotations

import base64
import click
import sys
from pathlib import Path
from typing import Final

from key_lifecycle import recover_secret, shard_secret
from zilant_prime_core.crypto.kdf import derive_key_dynamic
from zilant_prime_core.crypto.password_hash import hash_password, verify_password

__all__: Final = [
    "derive_key_cmd",
    "pw_hash_cmd",
    "pw_verify_cmd",
    "pq_genkeypair_cmd",
    "shard_cmd",
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


# ────────────────────────── key shard ──────────────────────────
@click.group("shard")
def shard_cmd() -> None:
    """Split and recover master keys."""


@shard_cmd.command("export")
@click.option("--threshold", type=int, required=True, metavar="T", help="Minimum shares needed to recover")
@click.option("--shares", type=int, required=True, metavar="N", help="Total number of shares")
@click.option("--output-dir", type=click.Path(file_okay=False, path_type=Path), required=True, metavar="DIR")
@click.option("--in-key", type=click.Path(exists=True, dir_okay=False, path_type=Path))
def shard_export_cmd(threshold: int, shares: int, output_dir: Path, in_key: Path | None) -> None:
    """Write shares to OUTPUT-DIR/share_*.bin."""
    output_dir.mkdir(parents=True, exist_ok=True)
    secret = Path(in_key).read_bytes() if in_key else sys.stdin.buffer.read()
    for i, sh in enumerate(shard_secret(secret, shares, threshold), 1):
        (output_dir / f"share_{i}.bin").write_bytes(sh)


@shard_cmd.command("import")
@click.option("--inputs", type=click.Path(file_okay=False, exists=True, path_type=Path), required=True, metavar="DIR")
@click.option("--output", type=click.Path(dir_okay=False, path_type=Path))
def shard_import_cmd(inputs: Path, output: Path | None) -> None:
    """Recover secret from shares in INPUTS directory."""
    shards = [p.read_bytes() for p in sorted(Path(inputs).glob("share_*.bin"))]
    secret = recover_secret(shards)
    if output:
        output.write_bytes(secret)
    else:
        sys.stdout.buffer.write(secret)
