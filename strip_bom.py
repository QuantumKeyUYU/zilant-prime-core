#!/usr/bin/env python3
import os
import sys

def strip_bom_from_file(path):
    """
    Убирает UTF-8 BOM (0xEF,0xBB,0xBF) в начале файла.
    """
    with open(path, 'rb') as f:
        data = f.read()
    if data.startswith(b'\xef\xbb\xbf'):
        with open(path, 'wb') as f:
            f.write(data[3:])
        print(f"Stripped BOM from {path}")

def main():
    if len(sys.argv) < 2:
        print("Usage: strip_bom.py <file_or_directory> [...]", file=sys.stderr)
        sys.exit(1)

    for target in sys.argv[1:]:
        if os.path.isfile(target):
            strip_bom_from_file(target)
        elif os.path.isdir(target):
            for root, _, files in os.walk(target):
                for name in files:
                    if name.lower().endswith(('.py', '.md', '.toml')):
                        strip_bom_from_file(os.path.join(root, name))
        else:
            print(f"Not found: {target}", file=sys.stderr)

if __name__ == "__main__":
    main()
