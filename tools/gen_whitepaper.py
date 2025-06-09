#!/usr/bin/env python3
"""
Сборка PDF‑whitepaper из Markdown‑глав проекта.

▪ docs/OVERVIEW.md   – (необяз.) вводная, будет первой главой
▪ docs/ARCH.md       – архитектура
▪ docs/THREATS.md    – модель угроз
▪ docs/whitepaper.yml – метаданные (title, author, …)

Выход: dist/whitepaper.pdf
Запуск: python tools/gen_whitepaper.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
DIST = ROOT / "dist"
DIST.mkdir(exist_ok=True)

# --- проваливаемся сразу, если pandoc не найден
if shutil.which("pandoc") is None:
    sys.exit("❌  pandoc not installed (apt/yum/winget)")

sources: list[str] = []
overview = DOCS / "OVERVIEW.md"
if overview.exists():
    sources.append(str(overview))
# обязательные главы
for part in ("ARCH.md", "THREATS.md"):
    file = DOCS / part
    if not file.exists():
        sys.exit(f"❌  missing {file.relative_to(ROOT)}")
    sources.append(str(file))

cmd = [
    "pandoc",
    *sources,
    "--pdf-engine=xelatex",  # кириллица без плясок
    "-V",
    "mainfont=Noto Sans",
    "-V",
    "monofont=Noto Sans Mono",
    "--toc",
    "-o",
    str(DIST / "whitepaper.pdf"),
]

meta = DOCS / "whitepaper.yml"
if meta.exists():
    cmd += ["--metadata-file", str(meta)]

print("🚀  running:", " ".join(cmd))
subprocess.run(cmd, check=True)
print("✅  whitepaper.pdf ready →", DIST / "whitepaper.pdf")
