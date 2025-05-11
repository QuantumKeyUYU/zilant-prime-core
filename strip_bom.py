#!/usr/bin/env python3
import os
import sys

def strip_bom(path):
    with open(path, 'rb') as f:
        data = f.read()
    if data.startswith(b'\xef\xbb\xbf'):
        print(f"Stripping BOM from {path}")
        with open(path, 'wb') as f:
            f.write(data[3:])

if __name__ == "__main__":
    for file in sys.argv[1:]:
        strip_bom(file)
