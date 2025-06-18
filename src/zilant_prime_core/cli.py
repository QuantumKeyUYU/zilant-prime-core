# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
from __future__ import annotations

import binascii
import os
import sys
from pathlib import Path
from typing import NoReturn, cast

import click

from container import pack_file, unpack_file
from zilant_prime_core.crypto.password_hash import hash_password, verify_password
from zilant_prime_core.utils import VaultClient
from zilant_prime_core.utils.anti_snapshot import detect_snapshot
from zilant_prime_core.utils.counter import increment_counter, read_counter
from zilant_prime_core.utils.device_fp import SALT_CONST, collect_hw_factors, compute_fp
from zilant_prime_core.utils.pq_crypto import Dilithium2Signature, Kyber768KEM
from zilant_prime_core.utils.recovery import DESTRUCTION_KEY_BUFFER, self_destruct
from zilant_prime_core.utils.screen_guard import ScreenGuardError, guard


# ────────────────────────── helpers ──────────────────────────
def _abort(msg: str, code: int = 1) -> NoReturn:  # ← NoReturn → mypy happy
    click.echo(msg)
    click.echo("Aborted")
    sys.exit(code)


def _ask_pwd(*, confirm: bool = False) -> str:
    pwd = cast(str, click.prompt("Password", hide_input=True, confirmation_prompt=confirm))
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
        old_file = container.parent / name_raw.decode()
        if old_file.exists():
            old_file.unlink()
    except Exception:
        pass


# ──────────────────────────────── CLI root ────────────────────────────────
@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--serve-metrics", type=int, metavar="PORT", help="Expose metrics on PORT")
@click.option("--vault-key", type=binascii.unhexlify, metavar="HEX", help="AES key for Vault")
@click.pass_context
def cli(ctx: click.Context, serve_metrics: int | None, vault_key: bytes | None) -> None:
    """Zilant Prime command‑line interface."""
    try:
        guard.assert_secure()
    except ScreenGuardError as exc:
        click.echo(f"Security check failed: {exc}", err=True)
        raise SystemExit(90)

    if serve_metrics:
        from zilant_prime_core.health import start_server

        start_server(serve_metrics)

    ctx.obj = {"vault_key": vault_key}


@cli.group()
def key() -> None:
    """Key management commands."""


@key.command("rotate")
@click.option("--days", type=int, required=True, metavar="DAYS", help="Rotation interval in days")
@click.option("--in-key", type=click.Path(exists=True, dir_okay=False, path_type=Path), required=True)
@click.option("--out-key", type=click.Path(dir_okay=False, path_type=Path), required=True)
def cmd_key_rotate(days: int, in_key: Path, out_key: Path) -> None:
    """Rotate master key and save the result."""
    from key_lifecycle import KeyLifecycle

    new_key = KeyLifecycle.rotate_master_key(in_key.read_bytes(), days)
    out_key.write_bytes(new_key)
    click.echo(out_key)


# ────────────────────────────── pack ──────────────────────────────
@cli.command("pack")
@click.argument("source", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("-o", "--output", metavar="OUT", type=click.Path(dir_okay=False, path_type=Path))
@click.option("-p", "--password", metavar="PWD|-", help='Password or "-" to prompt')
@click.option("--vault-path", metavar="VAULT_PATH", help="Path in HashiCorp Vault")
@click.option("--pq-pub", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--overwrite/--no-overwrite", default=False, show_default=True)
@click.pass_context
def cmd_pack(  # noqa: C901  (covered by extensive tests)
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

    # password handling
    if password == "-":
        pwd = _ask_pwd(confirm=True)
    elif password:
        pwd = password
    elif vault_path:
        try:
            vc = VaultClient(key=ctx.obj.get("vault_key") if ctx.obj else None)
            pwd = vc.get_secret(vault_path, key="password")
        except Exception as exc:
            click.echo(f"Vault error: {exc}", err=True)
            click.echo("Requesting password…", err=True)
            pwd = _ask_pwd(confirm=True)
    else:
        _abort("Missing password")

    # pack
    try:
        with metrics.track("pack"):
            if pq_pub:
                pack_file(source, dest, pwd.encode(), pq_public_key=pq_pub.read_bytes())
                blob: bytes | None = None
            else:
                blob = _pack_bytes(source, pwd, dest, overwrite)
    except FileExistsError:
        _abort(f"{dest.name} already exists")
    except Exception as exc:  # pragma: no cover
        _abort(f"Pack error: {exc}")

    # write container (non‑PQ branch)
    if blob is not None:
        tmp = dest.with_suffix(dest.suffix + ".tmp")
        try:
            with open(tmp, "wb") as fh:  # noqa: PTH123
                fh.write(blob)
            os.replace(tmp, dest)
            os.chmod(dest, 0o600)
        except Exception as exc:
            click.echo(f"Write error: {exc}", err=True)
            sys.exit(1)

    click.echo(dest)


# ────────────────────────────── unpack ──────────────────────────────
@cli.command("unpack")
@click.argument("container", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("-d", "--dest", metavar="DIR", type=click.Path(file_okay=False, path_type=Path))
@click.option("-p", "--password", metavar="PWD|-", help='Password or "-" to prompt')
@click.option("--pq-sk", type=click.Path(exists=True, dir_okay=False, path_type=Path))
def cmd_unpack(container: Path, dest: Path | None, password: str | None, pq_sk: Path | None) -> None:
    from zilant_prime_core.metrics import metrics

    pwd = _ask_pwd() if password == "-" else password or _abort("Missing password")
    out_dir = dest or container.parent
    if dest and out_dir.exists():
        _abort("Destination path already exists")
    if dest is None:
        _cleanup_old_file(container)

    try:
        with metrics.track("unpack"):
            if pq_sk:
                out_path = out_dir / container.stem
                unpack_file(container, out_path, pwd.encode(), pq_private_key=pq_sk.read_bytes())
                out = out_path
            else:
                out = _unpack_bytes(container, out_dir, pwd)
    except FileExistsError:
        _abort("Destination path already exists")
    except ValueError as ve:
        _abort("Container too small" if "too small" in str(ve).lower() else f"Unpack error: {ve}")
    except Exception as exc:  # pragma: no cover
        _abort(f"Unpack error: {exc}")

    try:
        os.chmod(out, 0o600)
    except Exception:
        pass

    click.echo(out)


# ─────────────────────── misc utility commands ───────────────────────
@cli.command("fingerprint")
def cmd_fingerprint() -> None:
    try:
        hw = collect_hw_factors()
        fp = compute_fp(hw, SALT_CONST)
        click.echo(fp.hex())
    except Exception as exc:  # pragma: no cover
        click.echo(f"Error computing fingerprint: {exc}", err=True)
        raise click.Abort()


@cli.command("check_counter")
def cmd_check_counter() -> None:
    click.echo(f"Current counter value: {read_counter()}")


@cli.command("incr_counter")
def cmd_incr_counter() -> None:
    increment_counter()
    click.echo(f"Counter incremented, new value: {read_counter()}")


@cli.command("sbom")
@click.option("--output", type=click.Path(dir_okay=False, path_type=Path), default="sbom.json")
@click.argument("target", type=click.Path(exists=True, path_type=Path), default=".")
def cmd_sbom(output: Path, target: Path) -> None:
    """Generate SBOM for TARGET into OUTPUT."""
    import subprocess

    subprocess.run(["syft", "packages", str(target), "-o", f"cyclonedx-json={output}"], check=True)
    click.echo(output)


@cli.command("check_snapshot")
def cmd_check_snapshot() -> None:
    try:
        if detect_snapshot():
            click.echo("Snapshot/rollback suspected!", err=True)
            raise click.Abort()
        click.echo("No snapshot detected.")
    except Exception as exc:
        click.echo(f"Error checking snapshot: {exc}", err=True)
        raise click.Abort()


@cli.command("self_destruct")
@click.argument("reason")
def cmd_self_destruct_cli(reason: str) -> None:
    self_destruct(reason, DESTRUCTION_KEY_BUFFER)
    click.echo("Self‑destruct completed. Decoy file generated.")


@cli.command("gen_kem_keys")
@click.option("--out-pk", type=click.Path(dir_okay=False, path_type=Path), required=True)
@click.option("--out-sk", type=click.Path(dir_okay=False, path_type=Path), required=True)
def cmd_gen_kem_keys(out_pk: Path, out_sk: Path) -> None:
    pk, sk = Kyber768KEM().generate_keypair()
    out_pk.write_bytes(pk)
    out_sk.write_bytes(sk)
    click.echo("KEM keypair generated.")


@cli.command("gen_sig_keys")
@click.option("--out-pk", type=click.Path(dir_okay=False, path_type=Path), required=True)
@click.option("--out-sk", type=click.Path(dir_okay=False, path_type=Path), required=True)
def cmd_gen_sig_keys(out_pk: Path, out_sk: Path) -> None:
    pk, sk = Dilithium2Signature().generate_keypair()
    out_pk.write_bytes(pk)
    out_sk.write_bytes(sk)
    click.echo("Signature keypair generated.")


# ───────── secure register / login (Argon2id) ─────────
@cli.command("register")
@click.argument("username")
@click.password_option(prompt=True, confirmation_prompt=True)
def cmd_register(username: str, password: str) -> None:
    store = Path(".opaque_store")
    store.mkdir(exist_ok=True)
    (store / f"{username}.pwd").write_text(hash_password(password))
    click.echo("registered")


@cli.command("login")
@click.argument("username")
@click.password_option(prompt=True)
def cmd_login(username: str, password: str) -> None:
    store_file = Path(".opaque_store") / f"{username}.pwd"
    ok = store_file.exists() and verify_password(store_file.read_text(), password)
    if not ok:
        click.echo("login failed", err=True)
        raise click.Abort()
    click.echo("login ok")


@cli.command("update")
def cmd_update() -> None:  # pragma: no cover
    click.echo("No updates available")


@cli.group()
def audit() -> None:
    """Audit log commands."""


@audit.command("verify")
def cmd_audit_verify() -> None:
    """Verify the integrity of the audit log."""
    from key_lifecycle import AuditLog

    log = AuditLog()
    if log.verify_log():
        click.echo("Audit log OK")
    else:
        click.echo("Audit log corrupted", err=True)
        raise click.Abort()


@cli.command()
@click.argument("shell", type=click.Choice(["bash", "zsh", "fish"]))
@click.pass_context
def complete(ctx: click.Context, shell: str) -> None:  # pragma: no cover
    import subprocess

    env = os.environ.copy()
    cmd_name = ctx.info_name or "zilant"
    env[f"{cmd_name.upper()}_COMPLETE"] = f"{shell}_source"
    res = subprocess.run([cmd_name], env=env, capture_output=True, text=True)
    click.echo(res.stdout)


# ───────── external sub‑commands (kdf, pw‑hash, …) ─────────
from zilant_prime_core.cli_commands import derive_key_cmd, pq_genkeypair_cmd, pw_hash_cmd, pw_verify_cmd  # noqa: E402

cli.add_command(derive_key_cmd)
cli.add_command(pw_hash_cmd)
cli.add_command(pw_verify_cmd)
cli.add_command(pq_genkeypair_cmd)

main = cli

if __name__ == "__main__":  # pragma: no cover
    cli()
