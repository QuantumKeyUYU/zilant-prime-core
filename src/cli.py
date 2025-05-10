# src/cli.py

"""
CLI для ZILANT Prime™.
"""
import sys
from pathlib import Path

import click

# Импортируем упаковку/распаковку
from pack import one_shot_pack
from pack import pack as _pack
from zil import unpack_zil

# ─────────────────────────────────────────────────────────────────────────── CLI ──


@click.group()
def cli() -> None:
    """ZILANT Prime CLI."""
    pass


@cli.command("pack")
@click.argument(
    "input_path",
    type=click.Path(exists=True, path_type=Path),
)
@click.option(
    "-o",
    "--output",
    "output_path",
    required=True,
    type=click.Path(path_type=Path),
    help="Куда записать .zil контейнер",
)
@click.option(
    "--one-shot",
    is_flag=True,
    help="Одношот-режим (удаляется после первого чтения).",
)
@click.option(
    "-p",
    "--password",
    "password",
    required=True,
    help="Пароль для шифрования",
)
@click.option(
    "--vdf-iters",
    "vdf_iters",
    type=int,
    default=0,
    show_default=True,
    help="Число VDF-итераций",
)
@click.option(
    "--meta",
    "meta",
    multiple=True,
    metavar="key=val",
    help="TLV-метаданные (можно повторять)",
)
def pack(
    input_path: Path,
    output_path: Path,
    one_shot: bool,
    password: str,
    vdf_iters: int,
    meta: tuple[str, ...],
) -> None:
    """
    Упаковать файл или папку в .zil контейнер.
    """
    # Парсим метаданные
    meta_dict: dict[str, str] = {}
    for m in meta:
        if "=" in m:
            k, v = m.split("=", 1)
            meta_dict[k] = v

    # Вызываем соответствующую функцию упаковки
    if one_shot:
        one_shot_pack(
            input_path,
            output_path,
            password=password,
            vdf_iters=vdf_iters,
            meta=meta_dict,
        )
    else:
        _pack(
            input_path,
            output_path,
            password=password,
            vdf_iters=vdf_iters,
            meta=meta_dict,
        )
    click.echo(f"created: {output_path.with_suffix('.zil')}")


@cli.command("unpack")
@click.argument(
    "input_path",
    type=click.Path(exists=True, path_type=Path),
)
@click.option(
    "-o",
    "--output",
    "output_path",
    type=click.Path(path_type=Path),
    help="Куда распаковать содержимое",
)
def unpack(
    input_path: Path,
    output_path: Path | None,
) -> None:
    """
    Распаковать .zil контейнер.
    """
    unpack_zil(input_path, output_path)
    click.echo("unpacked")


if __name__ == "__main__":
    cli(sys.argv[1:])
