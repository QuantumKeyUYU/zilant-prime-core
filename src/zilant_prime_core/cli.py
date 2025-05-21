#!/usr/bin/env python3
"""
Мини-CLI для упаковки/распаковки .zil-контейнеров.

❕ Изменения (v0.2):
    • Вынесено `prompt_password()` для переиспользования и тестируемости.
    • Логика confirm/overwrite вынесена в отдельную функцию `_handle_overwrite`.
    • Все пути, не покрытые тестами, оставлены без pragma – их теперь покрывает
      tests/test_cli_cover.py.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional, Sequence

import click

from zilant_prime_core.container.metadata import MetadataError
from zilant_prime_core.container.pack import pack as _pack_bytes
from zilant_prime_core.container.unpack import unpack as _unpack_bytes


# ────────────────────────── утилиты ──────────────────────────


def abort(message: str, exit_code: int = 1) -> None:
    """Вывести сообщение и завершить процесс."""
    click.echo(message)
    sys.exit(exit_code)


def prompt_password(confirm: bool = False) -> str:
    """Спрятанный ввод пароля с (опциональным) подтверждением."""
    return click.prompt("Password", hide_input=True, confirmation_prompt=confirm)


def _handle_overwrite(
    dest: Path,
    overwrite_flag: Optional[bool],
    prompt_fn=click.confirm,
) -> None:
    """
    Проверить, можно ли перезаписать файл `dest`:
        • если флага нет – задаём вопрос пользователю,
        • если `--no-overwrite` – немедленно abort,
        • если `--overwrite` – молча разрешаем.
    """
    if not dest.exists():
        return

    if overwrite_flag is None:  # задаём вопрос
        if not prompt_fn(f"{dest.name} already exists. Overwrite?"):
            abort("Aborted")
    elif overwrite_flag is False:  # --no-overwrite
        abort(f"{dest.name} already exists")
    # overwrite_flag is True → продолжаем молча


# ─────────────────────────────── CLI ────────────────────────────────


@click.group()
def cli() -> None:
    """Zilant Prime Core CLI."""
    pass


@cli.command("pack")
@click.argument("src", type=click.Path(exists=True, dir_okay=False))
@click.option("-p", "--password", default=None, help="Password, or '-' to prompt.")
@click.option(
    "-o", "--output", type=click.Path(dir_okay=False), default=None,
    help="Where to write the .zil archive.",
)
@click.option(
    "--overwrite/--no-overwrite",
    default=None,
    help="Whether to overwrite existing archive without prompting.",
)
def pack_cmd(
    src: str, *,
    password: Optional[str],
    output: Optional[str],
    overwrite: Optional[bool],
) -> None:
    """Упаковать файл в .zil-архив, зашифровав паролем."""
    src_path = Path(src)
    dest = Path(output) if output else src_path.with_suffix(".zil")

    # 1) overwrite-policy
    _handle_overwrite(dest, overwrite)

    # 2) пароль
    if password == "-":
        password = prompt_password(confirm=True)
    if not password:
        abort("Missing password")

    # 3) создаём контейнер
    try:
        container_bytes = _pack_bytes(src_path, password)
    except MetadataError as err:
        abort(str(err))
    except Exception as err:  # pragma: no cover – теоретически недостижимо
        abort(f"Packing error: {err}")

    # 4) пишем на диск
    try:
        dest.write_bytes(container_bytes)
    except Exception as err:  # pragma: no cover
        abort(f"Packing error: {err}")

    click.echo(str(dest))


@cli.command("unpack")
@click.argument("archive", type=click.Path(exists=True, dir_okay=False))
@click.option("-p", "--password", default=None, help="Password, or '-' to prompt.")
@click.option(
    "-d", "--dest", type=click.Path(file_okay=False), required=True,
    help="Directory to unpack into.",
)
def unpack_cmd(
    archive: str,
    *,
    password: Optional[str],
    dest: str,
) -> None:
    """Распаковать .zil-архив в указанную директорию."""
    archive_path = Path(archive)
    out_dir = Path(dest)

    # 1) папка назначения
    if out_dir.exists():
        abort(f"{out_dir.name} уже существует")

    # 2) пароль
    if password == "-":
        password = prompt_password()
    if not password:
        abort("Missing password")

    # 3) распаковываем
    try:
        created: Sequence[Path] | Path = _unpack_bytes(archive_path, out_dir, password)
    except MetadataError as err:
        abort(str(err))
    except Exception as err:  # pragma: no cover
        abort(f"Unpack error: {err}")

    # 4) выводим, что создали
    if isinstance(created, (list, tuple)):
        for p in created:
            click.echo(p)
    else:
        click.echo(created)


if __name__ == "__main__":
    cli()
