# pragma: no cover
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

from __future__ import annotations

import binascii
import os
import sys
from pathlib import Path
from typing import NoReturn

import click

from container import pack_file, unpack_file
from zilant_prime_core.cli_commands import derive_key_cmd, pq_genkeypair_cmd
from zilant_prime_core.utils import VaultClient
from zilant_prime_core.utils.anti_snapshot import detect_snapshot
from zilant_prime_core.utils.counter import increment_counter, read_counter
from zilant_prime_core.utils.device_fp import SALT_CONST, collect_hw_factors, compute_fp
from zilant_prime_core.utils.pq_crypto import Dilithium2Signature, Kyber768KEM
from zilant_prime_core.utils.recovery import DESTRUCTION_KEY_BUFFER, self_destruct
from zilant_prime_core.utils.screen_guard import ScreenGuardError, guard


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
@click.option("--serve-metrics", type=int, metavar="PORT", help="Expose metrics on PORT")
@click.option(
    "--vault-key",
    type=binascii.unhexlify,
    metavar="HEX",
    help="AES-key for vault",
)
@click.pass_context
def cli(ctx: click.Context, serve_metrics: int | None, vault_key: bytes | None) -> None:
    """Zilant Prime CLI."""
    try:
        guard.assert_secure()
    except ScreenGuardError as exc:
        click.echo(f"Security check failed: {exc}", err=True)
        raise SystemExit(90)
    if serve_metrics:
        from zilant_prime_core.health import start_server

        start_server(serve_metrics)
    # Initialization hooks are disabled in test mode
    ctx.obj = {"vault_key": vault_key}


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
@click.option("--pq-pub", type=click.Path(exists=True, dir_okay=False, path_type=Path), help="Kyber768 public key")
@click.option("--overwrite/--no-overwrite", default=False, show_default=True)
@click.pass_context
def cmd_pack(
    ctx: click.Context,
    source: Path,
    output: Path | None,
    password: str | None,
    vault_path: str | None,
    pq_pub: Path | None,
    overwrite: bool,
) -> None:
    from zilant_prime_core.metrics import metrics

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
            vault_client = VaultClient(key=ctx.obj.get("vault_key") if ctx.obj else None)
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
        with metrics.track("pack"):
            if pq_pub is not None:
                pack_file(source, dest, b"", pq_public_key=pq_pub.read_bytes())
            else:
                blob = _pack_bytes(source, pwd, dest, overwrite)
    except FileExistsError:
        _abort(f"{dest.name} already exists")
    except Exception as e:
        _abort(f"Pack error: {e}")

    if pq_pub is None:
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
@click.option("--pq-sk", type=click.Path(exists=True, dir_okay=False, path_type=Path), help="Kyber768 private key")
def cmd_unpack(container: Path, dest: Path | None, password: str | None, pq_sk: Path | None) -> None:
    from zilant_prime_core.metrics import metrics

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
        with metrics.track("unpack"):
            if pq_sk is not None:
                out_path = out_dir if out_dir.suffix else out_dir / container.stem
                unpack_file(container, out_path, b"", pq_private_key=pq_sk.read_bytes())
                out = out_path
            else:
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


@cli.command("gen_kem_keys")
@click.option("--out-pk", type=click.Path(dir_okay=False, path_type=Path), required=True)
@click.option("--out-sk", type=click.Path(dir_okay=False, path_type=Path), required=True)
def cmd_gen_kem_keys(out_pk: Path, out_sk: Path) -> None:
    """Generate Kyber768 keypair."""
    try:
        kem = Kyber768KEM()
        pk, sk = kem.generate_keypair()
        out_pk.write_bytes(pk)
        out_sk.write_bytes(sk)
        click.echo("KEM keypair generated.")
    except Exception as e:  # pragma: no cover - optional dependency
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


@cli.command("gen_sig_keys")
@click.option("--out-pk", type=click.Path(dir_okay=False, path_type=Path), required=True)
@click.option("--out-sk", type=click.Path(dir_okay=False, path_type=Path), required=True)
def cmd_gen_sig_keys(out_pk: Path, out_sk: Path) -> None:
    """Generate Dilithium2 signature keypair."""
    try:
        scheme = Dilithium2Signature()
        pk, sk = scheme.generate_keypair()
        out_pk.write_bytes(pk)
        out_sk.write_bytes(sk)
        click.echo("Signature keypair generated.")
    except Exception as e:  # pragma: no cover
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


cli.add_command(derive_key_cmd)
cli.add_command(pq_genkeypair_cmd)

main = cli  # alias for `python -m zilant_prime_core.cli`


@cli.command()
@click.argument("shell", type=click.Choice(["bash", "zsh", "fish"]))
@click.pass_context
def complete(ctx: click.Context, shell: str) -> None:
    """Generate shell completion script."""
    import subprocess

    env = os.environ.copy()
    cmd_name = ctx.info_name or "zilant"
    env[f"{cmd_name.upper()}_COMPLETE"] = f"{shell}_source"
    result = subprocess.run([cmd_name], env=env, capture_output=True, text=True)
    click.echo(result.stdout)


if __name__ == "__main__":  # pragma: no cover
    cli()
