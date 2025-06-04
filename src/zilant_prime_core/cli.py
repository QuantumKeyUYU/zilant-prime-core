# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import NoReturn

import click

from zilant_prime_core.utils.attest import attest_via_tpm
from zilant_prime_core.utils.file_monitor import start_file_monitor
from zilant_prime_core.utils.self_watchdog import init_self_watchdog


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
    attest_via_tpm()  # pragma: no cover
    init_self_watchdog(module_file=os.path.realpath(__file__), interval=60.0)  # pragma: no cover
    start_file_monitor(["sbom.json", "sealed_aes_key.bin", "config.yaml"])  # pragma: no cover


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

    tmp_path = dest.with_suffix(dest.suffix + ".tmp")
    try:
        with open(tmp_path, "wb") as f:
            f.write(blob)
        os.replace(tmp_path, dest)
        os.chmod(dest, 0o600)
    except Exception as e:
        _abort(f"Write error: {e}")

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

    try:
        os.chmod(out, 0o600)
    except Exception:
        pass

    click.echo(str(out))


main = cli  # alias for `python -m zilant_prime_core.cli`

if __name__ == "__main__":  # pragma: no cover
    cli()
