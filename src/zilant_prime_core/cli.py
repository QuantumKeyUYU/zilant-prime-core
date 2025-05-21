#!/usr/bin/env python3
import sys
from pathlib import Path

import click

from zilant_prime_core.container.pack import pack as _pack_bytes
from zilant_prime_core.container.unpack import unpack as _unpack_bytes
from zilant_prime_core.container.metadata import MetadataError


def abort(message: str, exit_code: int = 1) -> None:
    """Показываем сообщение в stdout и завершаем с кодом."""
    click.echo(message)
    sys.exit(exit_code)


@click.group()
def cli() -> None:
    """Zilant Prime Core CLI."""
    pass


@cli.command("pack")
@click.argument("src", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "-p",
    "--password",
    default=None,
    help="Password, or '-' to prompt (with confirmation).",
)
@click.option(
    "-o",
    "--output",
    "output",
    type=click.Path(dir_okay=False),
    default=None,
    help="Where to write the .zil archive.",
)
@click.option(
    "--overwrite/--no-overwrite",
    default=None,
    help="Whether to overwrite existing archive without prompting.",
)
def pack_cmd(src: str, password: str, output: str, overwrite: bool) -> None:
    """
    Упаковать файл или директорию в .zil-архив с шифрованием паролем.
    """
    src_path = Path(src)
    dest = Path(output) if output else src_path.with_suffix(".zil")

    # ── overwrite logic BEFORE password prompt ──
    if dest.exists():
        if overwrite is None:
            if not click.confirm(f"{dest.name} already exists. Overwrite?"):
                abort("Aborted")
        elif not overwrite:
            abort(f"{dest.name} already exists")

    # ── password prompt ──
    if password == "-":
        password = click.prompt("Password", hide_input=True, confirmation_prompt=True)
    if not password:
        abort("Missing password")

    # ── pack and write ──
    try:
        container_bytes = _pack_bytes(src_path, password)
    except MetadataError as e:
        abort(str(e))
    except Exception as e:
        abort(f"Packing error: {e}")

    try:
        dest.write_bytes(container_bytes)
    except Exception as e:
        abort(f"Packing error: {e}")

    click.echo(str(dest))


@cli.command("unpack")
@click.argument("archive", type=click.Path(exists=True, dir_okay=False))
@click.option("-p", "--password", default=None, help="Password, or '-' to prompt.")
@click.option(
    "-d",
    "--dest",
    "dest",
    type=click.Path(file_okay=False),
    required=True,
    help="Directory to unpack into.",
)
def unpack_cmd(archive: str, password: str, dest: str) -> None:
    """
    Распаковать .zil-архив в указанную директорию с расшифровкой паролем.
    """
    archive_path = Path(archive)
    out_dir = Path(dest)

    # если целевая папка уже есть — сразу ошибка на русском
    if out_dir.exists():
        abort(f"{out_dir.name} уже существует")

    # ── password prompt ──
    if password == "-":
        password = click.prompt("Password", hide_input=True)
    if not password:
        abort("Missing password")

    # ── unpack ──
    try:
        created = _unpack_bytes(archive_path, out_dir, password)
    except MetadataError as e:
        abort(str(e))
    except Exception as e:
        abort(f"Unpack error: {e}")

    if isinstance(created, (list, tuple)):
        for p in created:
            click.echo(str(p))
    else:
        click.echo(str(created))


if __name__ == "__main__":
    cli()
