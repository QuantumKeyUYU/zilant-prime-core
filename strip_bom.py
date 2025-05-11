#!/usr/bin/env python3
import sys

def strip_bom(path: str) -> None:
    with open(path, "rb") as f:
        data = f.read()
    if data.startswith(b'\xef\xbb\xbf'):
        with open(path, "wb") as f:
            f.write(data[3:])
        print(f"[BOM stripped] {path}")

if __name__ == "__main__":
    for filepath in sys.argv[1:]:
        strip_bom(filepath)
