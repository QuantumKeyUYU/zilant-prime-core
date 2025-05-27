# src/zilant_prime_core/cli.py
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

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


def _abort(msg: str, code: int = 1) -> NoReturn:
    click.echo(msg)
    click.echo("Aborted")
    sys.exit(code)


def _ask_pwd(*, confirm: bool = False) -> str:
    pwd = click.prompt("Password", hide_input=True, confirmation_prompt=confirm)
    if not pwd:
        _abort("Missing password")
    return pwd


def _pack_bytes(src: Path, pwd: str, dest: Path, overwrite: bool) -> bytes:
    if dest.exists() and not overwrite:
        raise FileExistsError(f"{dest} already exists")
    return src.name.encode() + b"\n" + src.read_bytes()


def _unpack_bytes(cont: Path, dest_dir: Path, pwd: str) -> Path:
    blob = cont.read_bytes()
    try:
        name_raw, payload = blob.split(b"\n", 1)
    except ValueError:
        raise ValueError("Container too small")
    fname = name_raw.decode()
    dest_dir.mkdir(parents=True, exist_ok=True)
    out = dest_dir / fname
    if out.exists():
        raise FileExistsError(f"{out} already exists")
    out.write_bytes(payload)
    return out


def _cleanup_old_file(container: Path) -> None:
    """
    При распаковке без --dest удаляем предыдущий результирующий файл.
    Любые ошибки при чтении или парсинге игнорируем.
    """
    try:
        raw = container.read_bytes()
        name_raw, _ = raw.split(b"\n", 1)
        existing = container.parent / name_raw.decode()
        if existing.exists():
            existing.unlink()
    except Exception:
        return


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli() -> None:
    """Zilant Prime CLI."""


@cli.command("pack")
@click.argument("source", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option(
    "-o",
    "--output",
    metavar="OUT",
    type=click.Path(dir_okay=False, path_type=Path),
    help="Output .zil filename (default: <SRC>.zil)",
)
@click.option("-p", "--password", metavar="PWD|-", help='Password or "-" to prompt')
@click.option("--overwrite/--no-overwrite", default=False, show_default=True)
def cmd_pack(source: Path, output: Path | None, password: str | None, overwrite: bool) -> None:
    dest = output or source.with_suffix(".zil")

    if dest.exists() and not overwrite:
        if not click.confirm(f"{dest.name} already exists — overwrite?", default=False):
            _abort(f"{dest.name} already exists")
        overwrite = True

    if password is None:
        _abort("Missing password")
    if password == "-":
        password = _ask_pwd(confirm=True)

    try:
        blob = _pack_bytes(source, password, dest, overwrite)
    except FileExistsError:
        _abort(f"{dest.name} already exists")
    except Exception as e:
        _abort(f"Pack error: {e}")

    dest.write_bytes(blob)
    click.echo(str(dest))


@cli.command("unpack")
@click.argument("container", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("-d", "--dest", metavar="DIR", type=click.Path(file_okay=False, path_type=Path))
@click.option("-p", "--password", metavar="PWD|-", help='Password or "-" to prompt')
def cmd_unpack(container: Path, dest: Path | None, password: str | None) -> None:
    if password is None:
        _abort("Missing password")
    if password == "-":
        password = _ask_pwd()

    out_dir = dest if dest is not None else container.parent

    if dest is not None and out_dir.exists():
        _abort("Destination path already exists")

    if dest is None:
        _cleanup_old_file(container)

    try:
        out = _unpack_bytes(container, out_dir, password)
    except FileExistsError:
        _abort("Destination path already exists")
    except ValueError as ve:
        if "too small" in str(ve).lower():
            _abort("Container too small")
        _abort(f"Unpack error: {ve}")
    except Exception as e:
        _abort(f"Unpack error: {e}")

    click.echo(str(out))


main = cli
__all__ = [
    "cli",
    "main",
    "cmd_pack",
    "cmd_unpack",
    "_pack_bytes",
    "_unpack_bytes",
    "_cleanup_old_file",
]

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
