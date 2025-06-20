# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
from __future__ import annotations

import binascii
import click
import json
import os
import sys
import time
import yaml  # type: ignore
from pathlib import Path
from typing import Any, NoReturn, cast

from container import pack_file, unpack_file
from key_lifecycle import recover_secret, shard_secret
from zilant_prime_core.crypto.password_hash import hash_password, verify_password
from zilant_prime_core.metrics import metrics
from zilant_prime_core.utils import VaultClient
from zilant_prime_core.utils.anti_snapshot import detect_snapshot
from zilant_prime_core.utils.counter import increment_counter, read_counter


def add_complete_flag() -> None:
    """Attach ``--install-completion`` option that prints the shell script."""

    def _callback(ctx: click.Context, param: click.Parameter, value: bool) -> None:
        if not value or ctx.resilient_parsing:
            return
        import subprocess

        shell = os.environ.get("SHELL", "bash").split("/")[-1]
        env = os.environ.copy()
        cmd_name = ctx.info_name or "zilant"
        env[f"{cmd_name.upper()}_COMPLETE"] = f"{shell}_source"
        out = subprocess.run([cmd_name], env=env, capture_output=True, text=True)
        click.echo(out.stdout)
        ctx.exit()

    cli.params.append(
        click.Option(
            ["--install-completion"],
            is_flag=True,
            expose_value=False,
            is_eager=True,
            help="Output shell completion script and exit",
            callback=_callback,
        )
    )


from zilant_prime_core.utils.device_fp import SALT_CONST, collect_hw_factors, compute_fp
from zilant_prime_core.utils.pq_crypto import Dilithium2Signature, Kyber768KEM
from zilant_prime_core.utils.recovery import DESTRUCTION_KEY_BUFFER, self_destruct
from zilant_prime_core.utils.screen_guard import ScreenGuardError, guard


# ────────────────────────── helpers ──────────────────────────
def _abort(msg: str, code: int = 1) -> NoReturn:  # ← NoReturn → mypy happy
    click.echo(msg)
    click.echo("Aborted")
    sys.exit(code)


def _emit(ctx: click.Context, data: dict[str, Any], fmt: str | None = None) -> None:
    """Print ``data`` using given or global format."""
    fmt = fmt or (ctx.obj.get("output") if ctx.obj else "text")
    if fmt == "json":
        click.echo(json.dumps(data, indent=2))
    elif fmt == "yaml":
        click.echo(yaml.safe_dump(data))
    else:
        click.echo(next(iter(data.values())))


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
@click.option("--metrics-port", type=int, metavar="PORT", help="Expose metrics on PORT")
@click.option("--vault-key", type=binascii.unhexlify, metavar="HEX", help="AES key for Vault")
@click.option(
    "--output",
    type=click.Choice(["text", "json", "yaml"], case_sensitive=False),
    default="text",
    show_default=True,
    help="Output format",
)
@click.pass_context
def cli(
    ctx: click.Context,
    metrics_port: int | None,
    vault_key: bytes | None,
    output: str,
) -> None:
    """Zilant Prime command‑line interface.

    Use ``zilant install-completion bash`` to enable shell autocompletion.

    Available HSM commands:
      ``hsm init``
      ``hsm seal``
      ``hsm unseal``
      ``hsm status``
    """
    try:
        guard.assert_secure()
    except ScreenGuardError as exc:
        click.echo(f"Security check failed: {exc}", err=True)
        raise SystemExit(90)

    if metrics_port:
        from zilant_prime_core.health import start_server

        start_server(metrics_port)

    ctx.obj = {"vault_key": vault_key, "output": output}


@cli.group()
def key() -> None:
    """Key management commands."""


@key.command("rotate")
@click.option("--days", type=int, required=True, metavar="DAYS", help="Rotation interval in days")
@click.option("--in-key", type=click.Path(exists=True, dir_okay=False, path_type=Path), required=True)
@click.option("--out-key", type=click.Path(dir_okay=False, path_type=Path), required=True)
@click.pass_context
@metrics.record_cli("key_rotate")
def cmd_key_rotate(ctx: click.Context, days: int, in_key: Path, out_key: Path) -> None:
    """Rotate master key and save the result."""
    from key_lifecycle import KeyLifecycle

    new_key = KeyLifecycle.rotate_master_key(in_key.read_bytes(), days)
    out_key.write_bytes(new_key)
    _emit(ctx, {"path": str(out_key)})


# ────────────────────────────── pack ──────────────────────────────
@cli.command("pack")
@click.argument("source", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("-o", "--output", metavar="OUT", type=click.Path(dir_okay=False, path_type=Path))
@click.option("-p", "--password", metavar="PWD|-", help='Password or "-" to prompt')
@click.option("--vault-path", metavar="VAULT_PATH", help="Path in HashiCorp Vault")
@click.option("--pq-pub", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--overwrite/--no-overwrite", default=False, show_default=True)
@click.pass_context
@metrics.record_cli("pack")
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
        start = time.perf_counter()
        with metrics.track("pack"):
            if pq_pub:
                pack_file(source, dest, pwd.encode(), pq_public_key=pq_pub.read_bytes())
                blob: bytes | None = None
            else:
                blob = _pack_bytes(source, pwd, dest, overwrite)
        metrics.encryption_duration_seconds.observe(time.perf_counter() - start)
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

    metrics.files_processed_total.inc()
    _emit(ctx, {"path": str(dest)})


# ────────────────────────────── unpack ──────────────────────────────
@cli.command("unpack")
@click.argument("container", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("-d", "--dest", metavar="DIR", type=click.Path(file_okay=False, path_type=Path))
@click.option("-p", "--password", metavar="PWD|-", help='Password or "-" to prompt')
@click.option("--pq-sk", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.pass_context
@metrics.record_cli("unpack")
def cmd_unpack(
    ctx: click.Context,
    container: Path,
    dest: Path | None,
    password: str | None,
    pq_sk: Path | None,
) -> None:
    from zilant_prime_core.metrics import metrics

    pwd = _ask_pwd() if password == "-" else password or _abort("Missing password")
    out_dir = dest or container.parent
    if dest and out_dir.exists():
        _abort("Destination path already exists")
    if dest is None:
        _cleanup_old_file(container)

    try:
        start = time.perf_counter()
        with metrics.track("unpack"):
            if pq_sk:
                out_path = out_dir / container.stem
                unpack_file(container, out_path, pwd.encode(), pq_private_key=pq_sk.read_bytes())
                out = out_path
            else:
                out = _unpack_bytes(container, out_dir, pwd)
        metrics.encryption_duration_seconds.observe(time.perf_counter() - start)
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

    metrics.files_processed_total.inc()
    _emit(ctx, {"path": str(out)})


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
@click.pass_context
def cmd_sbom(ctx: click.Context, output: Path, target: Path) -> None:
    """Generate SBOM for TARGET into OUTPUT."""
    import subprocess

    subprocess.run(["syft", "packages", str(target), "-o", f"cyclonedx-json={output}"], check=True)
    _emit(ctx, {"sbom": str(output)})


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
@click.pass_context
def cmd_audit_verify(ctx: click.Context) -> None:
    """Verify the integrity of the audit log."""
    from key_lifecycle import AuditLog

    log = AuditLog()
    ok = log.verify_log()
    if not ok:
        _emit(ctx, {"valid": False})
        if (ctx.obj or {}).get("output") == "text":
            click.echo("Audit log corrupted", err=True)
        raise click.Abort()
    _emit(ctx, {"valid": True})


@cli.group()
def timelock() -> None:
    """Time‑lock encryption helpers."""


@timelock.command("lock")
@click.option("--delay", type=int, required=True, metavar="SECONDS")
@click.option("--in-file", type=click.Path(exists=True, dir_okay=False, path_type=Path), required=True)
@click.option("--out-file", type=click.Path(dir_okay=False, path_type=Path), required=True)
def cmd_timelock_lock(delay: int, in_file: Path, out_file: Path) -> None:
    """Lock IN_FILE for the given DELAY."""
    from timelock import lock_file

    lock_file(str(in_file), str(out_file), delay)
    click.echo(str(out_file))


@timelock.command("unlock")
@click.option("--in-file", type=click.Path(exists=True, dir_okay=False, path_type=Path), required=True)
@click.option("--out-file", type=click.Path(dir_okay=False, path_type=Path), required=True)
def cmd_timelock_unlock(in_file: Path, out_file: Path) -> None:
    """Unlock IN_FILE previously locked via :func:`lock`."""
    from timelock import unlock_file

    unlock_file(str(in_file), str(out_file))
    click.echo(str(out_file))


@cli.group()
def ledger() -> None:
    """Audit ledger commands."""


@ledger.command("show")
@click.option("--last", "last_n", type=int, default=10, show_default=True, metavar="N")
def cmd_ledger_show(last_n: int) -> None:
    """Display last N ledger entries."""
    path = Path("audit-ledger.jsonl")
    if not path.exists():
        return
    lines = path.read_text(encoding="utf-8").splitlines()[-last_n:]
    for line in lines:
        click.echo(line)


@cli.group()
def attest() -> None:
    """TPM attestation helpers."""


@attest.command("simulate")
@click.option("--in-file", type=click.Path(exists=True, dir_okay=False, path_type=Path), required=True)
@click.pass_context
def cmd_attest_simulate(ctx: click.Context, in_file: Path) -> None:
    """Simulate TPM attestation of IN_FILE."""
    from attestation import simulate_tpm_attestation

    info = simulate_tpm_attestation(in_file.read_bytes())
    _emit(ctx, info, "json")


@cli.group()
def hsm() -> None:
    """Pseudo-HSM management commands."""


@hsm.command("init")
def hsm_init_cmd() -> None:
    """Initialize lock.json and counter.txt."""
    lock = Path("lock.json")
    counter = Path("counter.txt")
    if lock.exists() or counter.exists():
        raise click.ClickException("Pseudo-HSM already initialized")
    try:
        lock.write_text(json.dumps({"created": int(time.time())}))
        counter.write_text("0")
    except Exception as exc:  # pragma: no cover - filesystem errors
        raise click.ClickException(str(exc)) from exc
    click.echo("initialized")


@hsm.command("seal")
@click.option("--master-key", type=click.Path(exists=True, dir_okay=False, path_type=Path), required=True)
@click.option("--threshold", type=int, required=True, metavar="N")
@click.option("--shares", type=int, required=True, metavar="M")
@click.option("--output-dir", type=click.Path(file_okay=False, path_type=Path), required=True)
def hsm_seal_cmd(master_key: Path, threshold: int, shares: int, output_dir: Path) -> None:
    """Encrypt MASTER-KEY into shard files."""
    if shares < threshold or threshold < 2:
        raise click.UsageError("shares must be >= threshold >= 2")
    secret = master_key.read_bytes()
    pieces = shard_secret(secret, shares, threshold)
    output_dir.mkdir(parents=True, exist_ok=True)
    for i, piece in enumerate(pieces, 1):
        (output_dir / f"shard_{i}.hex").write_text(piece.hex())
    click.echo(f"{len(pieces)} shards written to {output_dir}")


@hsm.command("unseal")
@click.option("--input-dir", type=click.Path(exists=True, file_okay=False, path_type=Path), required=True)
@click.option("--output-file", type=click.Path(dir_okay=False, path_type=Path), required=True)
def hsm_unseal_cmd(input_dir: Path, output_file: Path) -> None:
    """Recover master key from shards in INPUT-DIR."""
    shard_paths = sorted(input_dir.glob("shard_*.hex"))
    if not shard_paths:
        raise click.ClickException("no shard files found")
    shards = []
    for p in shard_paths:
        try:
            shards.append(bytes.fromhex(p.read_text().strip()))
        except Exception as exc:
            raise click.ClickException(f"malformed shard file: {p}") from exc
    secret = recover_secret(shards)
    output_file.write_bytes(secret)
    click.echo(str(output_file))


@hsm.command("status")
def hsm_status_cmd() -> None:
    """Show lock file creation time and counter value."""
    lock = Path("lock.json")
    counter = Path("counter.txt")

    created: int | None = None
    counter_val: int | None = None

    if lock.exists():
        try:
            created = json.loads(lock.read_text()).get("created")
        except Exception as exc:  # pragma: no cover - invalid json
            raise click.ClickException("invalid lock.json") from exc

    if counter.exists():
        try:
            counter_val = int(counter.read_text().strip())
        except Exception as exc:  # pragma: no cover - invalid number
            raise click.ClickException("invalid counter file") from exc

    click.echo(json.dumps({"created": created, "counter": counter_val}))


@cli.command("install-completion")
@click.argument("shell", type=click.Choice(["bash", "zsh", "fish"]))
@click.pass_context
def install_completion(ctx: click.Context, shell: str) -> None:
    import subprocess

    env = os.environ.copy()
    cmd_name = ctx.info_name or "zilant"
    env[f"{cmd_name.upper()}_COMPLETE"] = f"{shell}_source"
    res = subprocess.run([cmd_name], env=env, capture_output=True, text=True)
    click.echo(res.stdout)


# ───────── external sub‑commands (kdf, pw‑hash, …) ─────────
from zilant_prime_core.cli_commands import (
    derive_key_cmd,
    hpke_cmd,
    pq_genkeypair_cmd,
    pw_hash_cmd,
    pw_verify_cmd,
    shard_cmd,
    stream_cmd,
)

cli.add_command(derive_key_cmd)
cli.add_command(pw_hash_cmd)
cli.add_command(pw_verify_cmd)
cli.add_command(pq_genkeypair_cmd)
key.add_command(shard_cmd)
cli.add_command(stream_cmd)
cli.add_command(hpke_cmd)
cli.add_command(hsm)

add_complete_flag()

main = cli

if __name__ == "__main__":  # pragma: no cover
    cli()
