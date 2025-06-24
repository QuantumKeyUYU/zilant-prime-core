import asyncio  # noqa: F401
import click
from pathlib import Path
from twisted.internet import reactor
from wormhole import create
from wormhole.errors import KeyFormatError  # noqa: F401

# ---------------------------------------------------------------------------
# Allow non-numeric codes like "root" by disabling wormhole's validator
try:  # pragma: no cover - optional internals may change
    import wormhole._nameplate as _np

    _np.validate_nameplate = lambda nameplate: None
    import wormhole._code as _cc

    _cc.validate_code = lambda code: None
except Exception:
    pass


@click.group()
def cli() -> None:
    """Transfer files using Magic Wormhole."""


@cli.command()
@click.argument("src", type=click.Path(exists=True))
@click.option("--relay", default="ws://localhost:4003", show_default=False)
def send(src: str, relay: str) -> None:
    """Send SRC via wormhole."""
    code = input().strip()
    w = create(appid="zilant", relay_url=relay, reactor=reactor)
    w.set_code(code)
    data = Path(src).read_bytes()
    w.send_message(Path(src).name.encode() + b"\n" + data)
    w.close()


@cli.command()
@click.option("--code", required=True)
@click.option("--relay", default="ws://localhost:4003", show_default=False)
@click.argument("directory", type=click.Path(file_okay=False), default=".")
def receive(code: str, relay: str, directory: str) -> None:
    """Receive a file using CODE."""
    w = create(appid="zilant", relay_url=relay, reactor=reactor)
    w.set_code(code)
    msg = w.get_message()
    w.close()
    name, data = msg.split(b"\n", 1)
    out = Path(directory) / name.decode()
    out.write_bytes(data)
