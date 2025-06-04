# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

from __future__ import annotations

import json
import os
import random
import shutil
import sys
import time
from pathlib import Path
from typing import NoReturn

import click

from zilant_prime_core.utils.attest import attest_via_tpm
from zilant_prime_core.utils.file_monitor import start_file_monitor
from zilant_prime_core.utils.rate_limit import RateLimiter
from zilant_prime_core.utils.self_watchdog import init_self_watchdog
from zilant_prime_core.utils.suspicion import log_suspicious_event
from zilant_prime_core.utils.tpm_counter import TpmCounterError, read_tpm_counter

_pack_rate_limiter = RateLimiter(max_calls=5, period=60.0)


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


def _maybe_sandbox() -> None:
    runsc_path = shutil.which("runsc")
    if runsc_path is not None and os.getenv("ZILANT_NO_SANDBOX") is None:
        cmd = ["runsc", "run", "--"] + sys.argv
        os.execvp(cmd[0], cmd)


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli() -> None:
    """Zilant Prime CLI."""
    runsc_path = shutil.which("runsc")
    if runsc_path is not None and os.getenv("ZILANT_NO_SANDBOX") is None:
        cmd = ["runsc", "run", "--"] + sys.argv
        os.execvp(cmd[0], cmd)
    attest_via_tpm()  # pragma: no cover
    try:
        counter = read_tpm_counter()
    except TpmCounterError as e:
        click.echo(f"TPM counter error: {e}", err=True)
        sys.exit(1)

    prev_file = Path.home() / ".zilant_prev_counter"
    if prev_file.exists():
        prev = int(prev_file.read_text())
        if counter <= prev:
            click.echo("TPM counter did not increase (possible rollback)! Exiting.", err=True)
            sys.exit(1)
    prev_file.write_text(str(counter))
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
@click.option(
    "--decoy-size",
    metavar="SIZE",
    type=int,
    default=None,
    help="If set, pad the payload to exactly SIZE bytes (decoy payload).",
)
def cmd_pack(source: Path, output: Path | None, password: str | None, overwrite: bool, decoy_size: int | None) -> None:
    dest = output or source.with_suffix(".zil")

    if dest.exists() and not overwrite:
        if not click.confirm(f"{dest.name} already exists — overwrite?", default=False):
            _abort(f"{dest.name} already exists")
        overwrite = True

    if password is None:
        _abort("Missing password")
    if password == "-":
        password = _ask_pwd(confirm=True)

    if not _pack_rate_limiter.allow():
        log_suspicious_event("rate_limit_exceeded", {"command": "pack"})
        _abort("Too many requests, try again later")

    try:
        if dest.exists() and not overwrite:
            raise FileExistsError(f"{dest} already exists")
        payload = source.read_bytes()
        if decoy_size is not None and decoy_size > 0:
            if len(payload) > decoy_size:
                _abort(f"Payload too large (got {len(payload)} bytes, but decoy-size={decoy_size})")
            padding = b"\x00" * (decoy_size - len(payload))
            payload = payload + padding
        header = source.name.encode() + b"\n"
        blob = header + payload
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

    time.sleep(random.uniform(0.05, 0.2))
    result = {"result": "OK", "canary": True}
    click.echo(json.dumps(result))


main = cli  # alias for `python -m zilant_prime_core.cli`

if __name__ == "__main__":  # pragma: no cover
    cli()
