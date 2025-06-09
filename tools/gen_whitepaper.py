import os
import shutil
import subprocess
import sys
from pathlib import Path

# Проверяем, что pandoc установлен
if not shutil.which("pandoc"):
    print("Error: pandoc is not installed", file=sys.stderr)
    sys.exit(1)

# Абсолютные пути
ROOT = Path(__file__).resolve().parent.parent
OUT_PDF = ROOT / "dist" / "whitepaper.pdf"
os.makedirs(OUT_PDF.parent, exist_ok=True)

# Список MD-файлов для сборки (ARCH, THREATS, и, если есть, Overview)
SRC_MD = [
    str(ROOT / "docs" / "ARCH.md"),
    str(ROOT / "docs" / "THREATS.md"),
]
OVERVIEW = ROOT / "docs" / "Overview.md"
if OVERVIEW.exists():
    SRC_MD.insert(0, str(OVERVIEW))

# Команда Pandoc
cmd = [
    "pandoc",
    "-o",
    str(OUT_PDF),
    "--pdf-engine=pdflatex",
    "--toc",
]

# Добавляем метаданные, если есть
META = ROOT / "docs" / "whitepaper.yml"
if META.exists():
    cmd += ["--metadata-file", str(META)]

# Последовательное добавление всех исходных MD
cmd += SRC_MD

# Запускаем сборку
try:
    subprocess.run(cmd, check=True)
    print(f"Whitepaper generated at {OUT_PDF}")
except subprocess.CalledProcessError as e:
    print("Error producing PDF.", file=sys.stderr)
    sys.exit(e.returncode)
