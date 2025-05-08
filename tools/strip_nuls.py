#!/usr/bin/env python3
"""
Strip NUL bytes from Python source files.
Usage: python tools/strip_nuls.py path/to/file1.py path/to/dir/*.py
"""
import sys
from pathlib import Path

def strip_file(path: Path):
    data = path.read_bytes().replace(b'\x00', b'')
    path.write_bytes(data)

if __name__ == "__main__":
    for arg in sys.argv[1:]:
        for p in Path(arg).parent.glob(Path(arg).name) if '*' in arg else [Path(arg)]:
            strip_file(p)
