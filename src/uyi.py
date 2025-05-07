#!/usr/bin/env python
"""
UYUBox CLI  –  упаковка и распаковка .zil‑контейнеров
Команды:
  uyi pack <infile> -o <outfile.zil> [options]
  uyi unpack <infile.zil> [options]
"""
from __future__ import annotations

import getpass
from pathlib import Path
from typing import Dict, Tuple

import click

from tlv import encode_tlv
from zil import create_zil, unpack_zil


def _prompt_passphrase() -> str:
    return getpass.getpass("Passphrase: ")


def _parse_meta(pairs: Tuple[str, ...]) -> Dict[int, bytes]:
    alias = {"mime": 0x01, "ver": 0x02}
    meta: Dict[int, bytes] = {}
    for pair in pairs:
        if "=" not in pair:
            raise click.BadParameter("--meta key=value expected")
        k, v = pair.split("=", 1)
        t = alias.get(k.lower())
        if t is None:
            if k.startswith("0x"):
                try:
                    t = int(k, 16)
                except ValueError:
                    raise click.BadParameter(f"Bad TLV type '{k}'")
            else:
                raise click.BadParameter(f"Unknown meta key '{k}'")
        meta[t] = v.encode()
    return meta


@click.group()
@click.version_option("0.1.0", prog_name="UYUBox CLI")
def cli() -> None:
    """Manage ZILANT Prime™ .zil containers."""
    pass


@cli.command()
@click.argument("infile", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("-o", "--outfile", type=click.Path(dir_okay=False, path_type=Path), required=True)
@click.option("-p", "--passphrase", help="Passphrase (prompted if omitted)")
@click.option("--vdf-iters", type=int, default=10, show_default=True)
@click.option("--one-shot/--multi", default=False, show_default=True)
@click.option("--meta", multiple=True, metavar="TYPE=VALUE", help="TLV metadata (mime, ver, or 0x##)")
def pack(
    infile: Path,
    outfile: Path,
    passphrase: str | None,
    vdf_iters: int,
    one_shot: bool,
    meta: Tuple[str, ...],
) -> None:
    if vdf_iters < 1:
        raise click.BadParameter("vdf-iters must be ≥1")
    if not passphrase:
        passphrase = _prompt_passphrase()

    meta_dict = _parse_meta(meta)
    click.echo(f"Packing {infile} → {outfile} (VDF={vdf_iters}, one-shot={one_shot})")
    data = infile.read_bytes()

    with click.progressbar(length=vdf_iters, label="Generating VDF") as bar:
        for _ in range(vdf_iters):
            bar.update(1)

    container = create_zil(
        data,
        passphrase,
        vdf_iters,
        metadata=meta_dict,
        one_shot=one_shot,
    )
    outfile.write_bytes(container)
    click.secho("✔ Packed successfully", fg="green")


@cli.command()
@click.argument("infile", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("-p", "--passphrase", help="Passphrase (prompted if omitted)")
@click.option("-o", "--outfile", type=click.Path(dir_okay=False, path_type=Path), help="Write plaintext to file")
def unpack(infile: Path, passphrase: str | None, outfile: Path | None) -> None:
    if not passphrase:
        passphrase = _prompt_passphrase()

    click.echo(f"Unpacking {infile} …")
    plaintext, meta = unpack_zil(infile.read_bytes(), passphrase)
    if plaintext is None:
        click.secho("✖ Decrypt / validate failed", fg="red")
        raise SystemExit(2)

    if outfile:
        outfile.write_bytes(plaintext)
        click.echo(f"✔ Plaintext written to {outfile}")
    else:
        click.echo(plaintext)

    if meta:
        click.echo("--- metadata ---")
        for t, v in meta.items():
            click.echo(f"0x{t:02X}: {v!r}")


if __name__ == "__main__":
    cli()
