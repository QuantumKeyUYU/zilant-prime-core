#!/usr/bin/env python3
import os

def strip_bom(path):
    with open(path, 'rb') as f:
        data = f.read()
    if data.startswith(b'\xef\xbb\xbf'):
        with open(path, 'wb') as f:
            f.write(data[3:])
        print(f"Stripped BOM: {path}")

if __name__ == "__main__":
    for root, _, files in os.walk("src"):
        for fn in files:
            strip_bom(os.path.join(root, fn))
