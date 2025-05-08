#!/usr/bin/env python3
"""
Strip all null bytes (\x00) from one or more files in place.
Usage:
    ./tools/strip_nuls.py path/to/file1 path/to/file2 ...
"""
import sys

def strip_nuls(path: str) -> None:
    data = open(path, 'rb').read().replace(b'\x00', b'')
    open(path, 'wb').write(data)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: strip_nuls.py <file1> [file2 ...]")
        sys.exit(1)
    for fn in sys.argv[1:]:
        strip_nuls(fn)
