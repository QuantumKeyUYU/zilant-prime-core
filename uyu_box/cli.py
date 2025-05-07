#!/usr/bin/env python3
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import click
from src.zil import create_zil, unpack_zil

@click.group()
def cli():
    """UYUBox — мгновенное .zil в один клик."""
    pass

@cli.command()
@click.argument("input",  type=click.Path(exists=True))
@click.argument("output", type=click.Path())
@click.option("-p", "--passphrase", prompt=True, hide_input=True, help="Пароль")
@click.option("-v", "--vdf",        default=1000, show_default=True, help="Итерации VDF")
@click.option("-t", "--tries",      default=3,    show_default=True, help="Число попыток")
@click.option("-m", "--metadata",   default="",   show_default=True, help="AAD (строка)")
def pack(input, output, passphrase, vdf, tries, metadata):
    """Упаковать INPUT-файл в OUTPUT.zil"""
    data = open(input, "rb").read()
    zil = create_zil(data, passphrase, vdf_iters=vdf, tries=tries, metadata=metadata.encode())
    with open(output, "wb") as f:
        f.write(zil)
    print(f"✅ Упаковано: {output}")

@cli.command()
@click.argument("input", type=click.Path(exists=True))
@click.option("-p", "--passphrase", prompt=True, hide_input=True, help="Пароль")
@click.option("-m", "--metadata",   default="",   show_default=True, help="AAD (строка)")
def unpack(input, passphrase, metadata):
    """Распаковать INPUT.zil и вывести в stdout"""
    container = open(input, "rb").read()
    pt, new_cont = unpack_zil(container, passphrase, metadata=metadata.encode())
    if pt is not None:
        # здесь обязательно decode, чтобы получить строку
        print(pt.decode("utf-8", errors="ignore"))
    else:
        click.secho("❌ Неверная passphrase или self-destruct.", fg="red")

if __name__ == "__main__":
    cli()
