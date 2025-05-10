import click

from src.zil import create_zil, unpack_zil


@click.group()
def main():
    """UYUBox — мгновенное .zil в один клик."""
    pass


@main.command()
@click.argument("input", type=click.Path(exists=True, dir_okay=False))
@click.argument("output", type=click.Path(dir_okay=False))
@click.option("-p", "--passphrase", required=True, help="Пароль для шифрования")
@click.option("-v", "--vdf-iters", default=100, help="Итераций VDF")
@click.option("-t", "--tries", default=3, help="Повторов VDF")
@click.option("-m", "--metadata", default="", help="Доп. данные (metadata)")
def pack(input, output, passphrase, vdf_iters, tries, metadata):
    """Упаковать INPUT → OUTPUT.zil"""
    data = open(input, "rb").read()
    z = create_zil(data, passphrase, vdf_iters, tries, metadata.encode())
    with open(output, "wb") as f:
        f.write(z)
    click.echo(f"✅ Упаковано: {output}")


@main.command()
@click.argument("input", type=click.Path(exists=True, dir_okay=False))
@click.option("-p", "--passphrase", required=True, help="Пароль для расшифровки")
@click.option("-m", "--metadata", default="", help="Доп. данные (metadata)")
def unpack(input, passphrase, metadata):
    """Распаковать INPUT.zil → stdout"""
    z = open(input, "rb").read()
    pt, _ = unpack_zil(z, passphrase, metadata.encode())
    # Выводим сырые байты в stdout
    import sys

    sys.stdout.buffer.write(pt)


if __name__ == "__main__":
    main()
