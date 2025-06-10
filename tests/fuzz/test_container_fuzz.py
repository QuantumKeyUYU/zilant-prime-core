import sys
import tempfile
from pathlib import Path

import atheris

from zilant_prime_core.container.pack import pack
from zilant_prime_core.container.unpack import UnpackError, unpack


def TestOneInput(data: bytes) -> None:
    with tempfile.NamedTemporaryFile(delete=False) as src:
        src.write(data)
        src.flush()
        try:
            cont = pack(Path(src.name), "pw")
            with tempfile.TemporaryDirectory() as out:
                try:
                    unpack(cont, out, "pw")
                except Exception:
                    pass
        except Exception:
            pass


def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
