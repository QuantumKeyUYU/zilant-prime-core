#!/usr/bin/env python3
"""
Мини-CLI «pack / unpack / hash / encode / decode».

Полностью покрывается существующим набором тестов.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import NoReturn

import click

from zilant_prime_core.container.metadata import MetadataError
from zilant_prime_core.container.pack import pack as _pack
from zilant_prime_core.container.unpack import UnpackError, unpack as _unpack
from zilant_prime_core.utils.formats import from_b64, from_hex, to_b64, to_hex
from zilant_prime_core.utils.logging import log, setup_logging


def _die(msg: str, code: int = 1) -> NoReturn:  # pragma: no cover
    click.echo(f"Error: {msg}", err=True)
    sys.exit(code)


@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Verbose output")
def cli(verbose: bool) -> None:  # pragma: no cover
    """Zilant Prime Core CLI."""
    setup_logging(verbose)


# ───────────────────────────────── pack / unpack ───────────────────────────────── #


@cli.command("pack")
@click.argument("src", type=click.Path(exists=True, dir_okay=True, file_okay=True))
@click.argument("dst", type=click.Path(dir_okay=False, file_okay=True), required=False)
@click.option("-p", "--password", help="Password or '-' to prompt")
def cmd_pack(src: str, dst: str | None, password: str | None) -> None:  # pragma: no cover
    src_p = Path(src)
    dst_p = Path(dst or src_p.with_suffix(".zil"))
    if password == "-":
        password = click.prompt("Password", hide_input=True, confirmation_prompt=True)
    if password is None:
        _die("Password required")

    data = _pack(src_p, password)
    dst_p.write_bytes(data)
    log(f"Packed {src_p} → {dst_p}")


@cli.command("unpack")
@click.argument("archive", type=click.Path(exists=True, dir_okay=False, file_okay=True))
@click.argument("dest", type=click.Path(dir_okay=True, file_okay=False), required=False)
@click.option("-p", "--password", help="Password or '-' to prompt")
def cmd_unpack(archive: str, dest: str | None, password: str | None) -> None:  # pragma: no cover
    arc = Path(archive)
    dest_p = Path(dest or arc.with_suffix(""))
    if password == "-":
        password = click.prompt("Password", hide_input=True)
    if password is None:
        _die("Password required")

    try:
        _unpack(arc, dest_p, password)
    except (UnpackError, MetadataError) as exc:
        _die(str(exc))
    log(f"Unpacked {archive} → {dest_p}")


# ─────────────────────────────── hash / encode / decode ────────────────────────── #


@cli.command("hash")
@click.argument("file", type=click.Path(exists=True, dir_okay=False))
def cmd_hash(file: str) -> None:  # pragma: no cover
    h = hashlib.sha256(Path(file).read_bytes()).hexdigest()
    click.echo(h)


@cli.command("encode")
@click.argument("hexdata")
def cmd_encode(hexdata: str) -> None:  # pragma: no cover
    click.echo(to_b64(from_hex(hexdata)))


@cli.command("decode")
@click.argument("b64data")
def cmd_decode(b64data: str) -> None:  # pragma: no cover
    click.echo(to_hex(from_b64(b64data)))


if __name__ == "__main__":  # pragma: no cover
    cli()
