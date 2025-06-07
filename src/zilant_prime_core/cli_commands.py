# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core Contributors
"""Extra CLI commands."""

from __future__ import annotations

import base64
from pathlib import Path

import click

from zilant_prime_core.crypto_core import derive_key_argon2id


@click.command("derive-key")
@click.option("--mem", "mem_cost", type=int, default=512 * 1024, show_default=True)
@click.option("--time", "time_cost", type=int, default=4, show_default=True)
@click.argument("password")
@click.argument("salt", type=click.Path(exists=True, dir_okay=False, path_type=Path))
def derive_key_cmd(password: str, salt: Path, mem_cost: int, time_cost: int) -> None:
    """Derive Argon2id key."""
    key = derive_key_argon2id(password.encode(), salt.read_bytes(), mem_cost, time_cost)
    click.echo(base64.b64encode(key).decode())
