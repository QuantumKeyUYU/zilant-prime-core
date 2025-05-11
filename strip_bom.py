#!/usr/bin/env python3
import sys

def strip_bom(path: str) -> None:
    with open(path, "rb") as f:
        data = f.read()
    bom = b'\xef\xbb\xbf'
    if data.startswith(bom):
        with open(path, "wb") as f:
            f.write(data[len(bom):])

if __name__ == "__main__":
    for filepath in sys.argv[1:]:
        strip_bom(filepath)
