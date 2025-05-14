import sys
from pathlib import Path
import struct

import click

from zilant_prime_core.container.pack import pack as _pack_bytes
from zilant_prime_core.container.unpack import unpack as _unpack_bytes
from zilant_prime_core.container.metadata import deserialize_metadata
from zilant_prime_core.utils.constants import HEADER_FMT


def _prompt_password_twice() -> str | None:
    pw1 = click.prompt("Password", hide_input=True)
    pw2 = click.prompt("Confirm ", hide_input=True)
    return pw1 if pw1 == pw2 else None


@click.group()
def cli() -> None:
    """🪄 Compress → Encrypt → Seal → *.zil"""
    pass


@cli.command("pack")
@click.argument("src", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option(
    "-p", "--password", "password_opt", default="-",
    help="'-' ⇒ интерактивный ввод два раза"
)
@click.option("-o", "--output", type=click.Path(dir_okay=False, path_type=Path))
def cmd_pack(src: Path, password_opt: str, output: Path | None):
    """Запаковать SRC → SRC.zil (или --output)."""
    if password_opt == "-":
        pw = _prompt_password_twice()
        if pw is None:
            click.echo("Passwords do not match!")
            sys.exit(1)
    else:
        pw = password_opt

    container = _pack_bytes(src, password=pw)
    dst = output or src.with_suffix(".zil")
    dst.write_bytes(container)
    click.echo(dst)


@cli.command("unpack")
@click.argument("container", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option(
    "-p", "--password", "password_opt", default="-",
    help="'-' ⇒ интерактивный ввод пароля"
)
@click.option(
    "-d", "--dir", "out_dir",
    type=click.Path(file_okay=False, path_type=Path),
    default="."
)
@click.option("--overwrite", is_flag=True, help="Разрешить перезапись файлов")
def cmd_unpack(container: Path, password_opt: str, out_dir: Path, overwrite: bool):
    """Распаковать CONTAINER → файл в --dir."""

    # 1) читаем и разбираем метаданные, чтобы узнать имя выходного файла
    raw = Path(container).read_bytes()
    magic, ver, mlen, plen, slen = struct.unpack_from(HEADER_FMT, raw)
    off = struct.calcsize(HEADER_FMT)
    meta_blob = raw[off : off + mlen]
    meta = deserialize_metadata(meta_blob)
    filename = meta["filename"]
    out_path = out_dir / filename

    # 2) проверяем существование до распаковки
    if out_path.exists():
        if not overwrite:
            click.echo("File already exists, use --overwrite.")
            sys.exit(1)
        else:
            out_path.unlink()

    # 3) читаем пароль
    if password_opt == "-":
        pw = click.prompt("Password", hide_input=True)
    else:
        pw = password_opt

    # 4) собственно распаковка
    extracted = _unpack_bytes(container, output_dir=out_dir, password=pw)
    click.echo(extracted)


if __name__ == "__main__":
    cli()
