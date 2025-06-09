import os
import shutil
import subprocess
import sys
from pathlib import Path

if not shutil.which("pandoc"):
    print("Error: pandoc is not installed", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
SRC_MD = ["docs/ARCH.md", "docs/THREATS.md"]
OVERVIEW = ROOT / "docs" / "Overview.md"
if OVERVIEW.exists():
    SRC_MD.insert(0, str(OVERVIEW))
OUT_PDF = ROOT / "dist" / "whitepaper.pdf"
os.makedirs(OUT_PDF.parent, exist_ok=True)
cmd = [
    "pandoc",
    "-o",
    str(OUT_PDF),
    "--pdf-engine=pdflatex",
    "--toc",
]
meta = ROOT / "docs" / "whitepaper.yml"
if meta.exists():
    cmd += ["--metadata-file", str(meta)]
cmd += SRC_MD
subprocess.run(cmd, check=True)
print(f"Whitepaper generated at {OUT_PDF}")
