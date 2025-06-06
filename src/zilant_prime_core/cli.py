# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import NoReturn

import click

from zilant_prime_core.utils import VaultClient
from zilant_prime_core.utils.anti_snapshot import detect_snapshot
from zilant_prime_core.utils.counter import increment_counter, read_counter
from zilant_prime_core.utils.device_fp import (
    SALT_CONST,
    collect_hw_factors,
    compute_fp,
    get_device_fingerprint,
)
from zilant_prime_core.utils.recovery import DESTRUCTION_KEY_BUFFER, self_destruct
from zilant_prime_core.utils.self_watchdog import init_self_watchdog
from zilant_prime_core.utils.shard_secret import recover_secret, split_secret


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
    # Initialization hooks are disabled in test mode
    pass


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
@click.option("--vault-path", metavar="VAULT_PATH", help="Путь до секрета в HashiCorp Vault")
@click.option("--overwrite/--no-overwrite", default=False, show_default=True)
def cmd_pack(
    source: Path,
    output: Path | None,
    password: str | None,
    vault_path: str | None,
    overwrite: bool,
) -> None:
    dest = output or source.with_suffix(".zil")

    if dest.exists() and not overwrite:
        if not click.confirm(f"{dest.name} already exists — overwrite?", default=False):
            _abort(f"{dest.name} already exists")
        overwrite = True

    pwd = password
    if pwd is not None:
        if pwd == "-":
            pwd = _ask_pwd(confirm=True)
    elif vault_path is not None:
        try:
            vault_client = VaultClient()
            pwd = vault_client.get_secret(vault_path, key="password")
        except Exception as exc:
            click.echo(f"Vault error: {exc}", err=True)
            click.echo(
                "Не удалось получить пароль из Vault, запрашиваю вручную …",
                err=True,
            )
            pwd = _ask_pwd(confirm=True)
    else:
        _abort("Missing password")

    if pwd is None:
        _abort("Missing password")

    try:
        blob = _pack_bytes(source, pwd, dest, overwrite)
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


@cli.command("fingerprint")
def cmd_fingerprint() -> None:
    """Output device fingerprint as hex string."""
    try:
        hw = collect_hw_factors()
        fp = compute_fp(hw, SALT_CONST)
        click.echo(fp.hex())
    except Exception as e:  # pragma: no cover - rare failure
        click.echo(f"Error computing fingerprint: {e}", err=True)
        raise click.Abort()


@cli.command("check_counter")
def cmd_check_counter() -> None:
    """Display the current hidden counter value."""
    try:
        ctr = read_counter()
        click.echo(f"Current counter value: {ctr}")
    except Exception as e:
        click.echo(f"Error reading counter: {e}", err=True)
        raise click.Abort()


@cli.command("incr_counter")
def cmd_incr_counter() -> None:
    """Increment the hidden counter and show the new value."""
    try:
        increment_counter()
        new_ctr = read_counter()
        click.echo(f"Counter incremented, new value: {new_ctr}")
    except Exception as e:
        click.echo(f"Error incrementing counter: {e}", err=True)
        raise click.Abort()


@cli.command("check_snapshot")
def cmd_check_snapshot() -> None:
    """Check for snapshot/rollback and exit with error if detected."""
    try:
        suspected = detect_snapshot()
        if suspected:
            click.echo("Snapshot/rollback suspected!", err=True)
            raise click.Abort()
        click.echo("No snapshot detected.")
    except Exception as e:
        click.echo(f"Error checking snapshot: {e}", err=True)
        raise click.Abort()


@cli.command("self_destruct")
@click.argument("reason", type=str)
def cmd_self_destruct_cli(reason: str) -> None:
    """Trigger self-destruction sequence with *reason*."""
    try:
        self_destruct(reason, DESTRUCTION_KEY_BUFFER)
        click.echo("Self-destruct completed. Decoy file generated.")
    except Exception as e:
        click.echo(f"Self-destruct failed: {e}", err=True)
        raise click.Abort()


main = cli  # alias for `python -m zilant_prime_core.cli`

if __name__ == "__main__":  # pragma: no cover
    cli()
