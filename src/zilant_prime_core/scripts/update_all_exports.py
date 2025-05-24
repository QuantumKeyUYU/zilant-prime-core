#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

import os
import ast
import sys
__all__ = [
    'SKIP_DIRS',
    'collect_public_names',
    'find_all_assign',
    'main',
    'update_module',
]




SKIP_DIRS = {'.git', '__pycache__', 'build', 'dist', '.venv'}

def collect_public_names(tree: ast.AST) -> list[str]:
    names = []
    for node in tree.body:
        # классы и функции
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith('_'):
                names.append(node.name)
        # топ-левел переменные через простые присваивания
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and not t.id.startswith('_') and t.id != "__all__":
                    names.append(t.id)
    return sorted(set(names))

def find_all_assign(tree: ast.AST) -> ast.Assign | None:
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "__all__":
                    return node
    return None

def update_module(path: str):
    src = open(path, encoding='utf-8').read()
    tree = ast.parse(src, path)
    public = collect_public_names(tree)
    if not public:
        return

    all_node = find_all_assign(tree)
    # формируем новый блок __all__
    block = "__all__ = [\n" + "".join(f"    '{name}',\n" for name in public) + "]\n\n"

    lines = src.splitlines(keepends=True)
    if all_node:
        # удалить старый __all__ (по номерам линий)
        start, end = all_node.lineno - 1, all_node.end_lineno
        del lines[start:end]
        lines.insert(start, block)
    else:
        # вставить сразу после shebang/encoding и импортов
        idx = 0
        for i, L in enumerate(lines):
            if L.startswith('#!') or L.startswith('# -*-') or L.startswith('import') or L.startswith('from'):
                idx = i + 1
            else:
                break
        lines.insert(idx, block)

    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"⇒ Updated __all__ in {path}")

def main(root_dirs: list[str]):
    for root in root_dirs:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fn in filenames:
                if not fn.endswith('.py'):
                    continue
                update_module(os.path.join(dirpath, fn))

if __name__ == "__main__":
    roots = sys.argv[1:] if len(sys.argv) > 1 else ['src/zilant_prime_core']
    main(roots)
