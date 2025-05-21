import sys
from pathlib import Path

import click

from zilant_prime_core.container.pack import pack as _pack_bytes
from zilant_prime_core.container.unpack import unpack as _unpack_bytes
from zilant_prime_core.container.metadata import MetadataError


@click.group()
def cli():
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
def pack_cmd(src, password, output, overwrite):
    src_path = Path(src)
    dest = Path(output) if output else src_path.with_suffix(".zil")

    # ── overwrite logic BEFORE password prompt ──
    if dest.exists():
        if overwrite is None:
            if not click.confirm(f"{dest.name} already exists. Overwrite?"):
                raise click.ClickException("Aborted")
        elif not overwrite:
            raise click.ClickException(f"{dest.name} already exists")

    # ── password prompt ──
    if password == "-":
        password = click.prompt("Password", hide_input=True, confirmation_prompt=True)
    if not password:
        raise click.ClickException("Missing password")

    # ── pack and write ──
    try:
        container_bytes = _pack_bytes(src_path, password)
    except MetadataError as e:
        raise click.ClickException(str(e))
    except Exception as e:
        raise click.ClickException(f"Packing error: {e}")

    try:
        dest.write_bytes(container_bytes)
    except Exception as e:
        raise click.ClickException(f"Packing error: {e}")

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
def unpack_cmd(archive, password, dest):
    archive_path = Path(archive)
    out_dir = Path(dest)

    if password == "-":
        password = click.prompt("Password", hide_input=True)
    if not password:
        raise click.ClickException("Missing password")

    try:
        created = _unpack_bytes(archive_path, out_dir, password)
    except MetadataError as e:
        raise click.ClickException(str(e))
    except Exception as e:
        raise click.ClickException(f"Unpack error: {e}")

    if isinstance(created, (list, tuple)):
        for p in created:
            click.echo(str(p))
    else:
        click.echo(str(created))


if __name__ == "__main__":
    cli()
