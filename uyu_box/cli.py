import os, sys
import click
from src.kdf import derive_key
from src.zil import create_zil, unpack_zil

@click.group()
def cli(): pass

@cli.command()
@click.argument("input", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
@click.option("-p","--passphrase", required=True)
@click.option("-v","--vdf-iters", default=100)
@click.option("-t","--tries", default=1)
@click.option("-m","--meta", default="", help="Original filename")
def pack(input, output, passphrase, vdf_iters, tries, meta):
    data = open(input,"rb").read()
    cont = create_zil(data, passphrase, vdf_iters, tries, metadata=meta.encode())
    with open(output,"wb") as f: f.write(cont)
    click.echo(f"✅ Packed: {output}")

@cli.command()
@click.argument("input", type=click.Path(exists=True))
@click.option("-p","--passphrase", required=True)
@click.option("-m","--meta", default="", help="Original filename")
def unpack(input, passphrase, meta):
    cont = open(input,"rb").read()
    pt, _ = unpack_zil(cont, passphrase, metadata=meta.encode())
    if pt is None:
        click.echo("❌ Wrong passphrase or self-destruct.")
        sys.exit(1)
    # выводим в stdout:
    sys.stdout.buffer.write(pt)

if __name__ == "__main__":
    cli()
