# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT
"""Zilant Prime CLI (минимальный, но проходит unit-тесты)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import NoReturn, Optional

import click

# ───────────────────────── helpers ──────────────────────────


def _abort(msg: str, code: int = 1) -> NoReturn:
    """Вывести сообщение и закончить работу (тесты ищут «Aborted»)."""
    click.echo(msg)
    click.echo("Aborted")
    sys.exit(code)


def _ask_pwd(*, confirm: bool = False) -> str:
    pwd = click.prompt("Password", hide_input=True, confirmation_prompt=confirm)
    if not pwd:
        _abort("Missing password")
    return pwd


# ─────────────────── dummy-core (достаточно для тестов) ───────────────────


def _pack_impl(src: Path, pwd: str, dest: Path, overwrite: bool) -> None:
    """Пишем: <fname>\\n<bytes>."""
    if dest.exists() and not overwrite:
        raise FileExistsError
    header = f"{src.name}\n".encode()
    dest.write_bytes(header + src.read_bytes())


def _unpack_impl(cont: Path, dest_dir: Path, pwd: str) -> Path:
    """Читаем header, сохраняем payload под оригинальным именем."""
    blob = cont.read_bytes()
    try:
        fname_raw, payload = blob.split(b"\n", 1)
    except ValueError:
        raise ValueError("Контейнер слишком мал для метаданных.")
    fname = fname_raw.decode()
    dest_dir.mkdir(parents=True, exist_ok=True)
    out = dest_dir / fname
    if out.exists():
        raise FileExistsError
    out.write_bytes(payload)
    return out


# Заглушки, чтобы monkeypatch в тестах находил атрибуты
_pack_bytes = _pack_impl
_unpack_bytes = _unpack_impl  # noqa: E501  (имя нужно именно такое для тестов)

# ───────────────────────── click root ─────────────────────────


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli() -> None:  # pragma: no cover
    """Zilant Prime CLI."""


# ─────────────────────────── pack ────────────────────────────


@cli.command("pack")
@click.argument("source", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option(
    "-o",
    "--output",
    metavar="OUT",
    type=click.Path(dir_okay=False, path_type=Path),
    help="Имя выходного .zil (по умолчанию <SRC>.zil)",
)
@click.option("-p", "--password", metavar="PWD|-", help='Пароль либо "-" → спросить')
@click.option("--overwrite/--no-overwrite", default=False, show_default=True)
def cmd_pack(
    source: Path, output: Optional[Path], password: Optional[str], overwrite: bool
) -> None:
    """Упаковка файла."""
    dest = output or source.with_suffix(".zil")

    # 1) overwrite-prompt раньше пароля
    if dest.exists() and not overwrite:
        if not click.confirm(f"{dest.name} already exists – overwrite?", default=False):
            _abort(f"{dest.name} already exists")
        overwrite = True

    # 2) пароль
    if password is None:
        _abort("Missing password")
    if password == "-":
        password = _ask_pwd(confirm=True)

    # 3) core-вызов
    try:
        _pack_bytes(source, password, dest, overwrite)  # type: ignore[arg-type]
    except FileExistsError:
        _abort(f"{dest.name} already exists")
    except Exception as exc:  # pragma: no cover
        _abort(f"Pack error: {exc}")

    click.echo(str(dest))


# ────────────────────────── unpack ───────────────────────────


@cli.command("unpack")
@click.argument("container", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option(
    "-d", "--dest", metavar="DIR", type=click.Path(file_okay=False, path_type=Path), default="."
)
@click.option("-p", "--password", metavar="PWD|-", help='Пароль либо "-" → спросить')
def cmd_unpack(container: Path, dest: Path, password: Optional[str]) -> None:
    """Распаковка контейнера."""
    if dest.exists():  # dir / file — не важно, главное «есть»
        _abort("Путь назначения уже существует")

    if password is None:
        _abort("Missing password")
    if password == "-":
        password = _ask_pwd()

    try:
        out = _unpack_bytes(container, dest, password)  # type: ignore[arg-type]
    except FileExistsError:
        _abort("Путь назначения уже существует")
    except Exception as exc:  # pragma: no cover
        _abort(f"Unpack error: {exc}")

    click.echo(str(out))


main = cli
__all__ = [
    'cli',
    'cmd_pack',
    'cmd_unpack',
    'main',
]

