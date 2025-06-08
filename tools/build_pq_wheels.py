import glob
import subprocess
from pathlib import Path

WHL_DIR = Path("whl")
WHL_DIR.mkdir(exist_ok=True)

for src in glob.glob("third_party/pqclean/**/kyber768*", recursive=True):
    subprocess.run(
        ["python", "setup.py", "bdist_wheel", "--plat-name", "manylinux_x86_64"],
        cwd=src,
        check=True,
    )
    for wheel in Path(src, "dist").glob("*.whl"):
        wheel.rename(WHL_DIR / wheel.name)
