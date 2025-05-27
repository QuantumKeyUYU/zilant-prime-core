#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

__all__ = [
    "EXCLUDE_DIRS",
    "HEADER",
    "has_spdx_header",
    "main",
    "process_file",
]


# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

import os
import sys

HEADER = [
    "# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors",
    "# SPDX-License-Identifier: MIT",
    "",
]

EXCLUDE_DIRS = {".git", "__pycache__", "build", "dist", ".venv"}


def has_spdx_header(lines):
    # Проверяем первые 5 строк на наличие SPDX
    for line in lines[:5]:
        if "SPDX-License-Identifier" in line:
            return True
    return False


def process_file(path):
    with open(path, "r+", encoding="utf-8") as f:
        lines = f.readlines()
        if has_spdx_header(lines):
            return False

        # Определяем, куда вставить (после shebang или encoding)
        insert_at = 0
        if lines and lines[0].startswith("#!"):
            insert_at = 1
        if len(lines) > insert_at and lines[insert_at].startswith("# -*-"):
            insert_at += 1

        new_lines = lines[:insert_at] + [h + "\n" for h in HEADER] + lines[insert_at:]
        f.seek(0)
        f.truncate()
        f.writelines(new_lines)
        return True


def main(root_dirs):
    added = 0
    for root in root_dirs:
        for dirpath, dirnames, filenames in os.walk(root):
            # исключаем служебные каталоги
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
            for fname in filenames:
                if not fname.endswith(".py"):
                    continue
                path = os.path.join(dirpath, fname)
                if process_file(path):
                    print(f"Added SPDX header to {path}")
                    added += 1
    print(f"\nTotal headers added: {added}")


if __name__ == "__main__":
    roots = sys.argv[1:] if len(sys.argv) > 1 else ["src", "tests"]
    main(roots)
