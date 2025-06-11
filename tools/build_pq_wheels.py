import glob
import os
import subprocess
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    pq_dir = Path(os.getenv("PQ_DIR", root / "third_party" / "pqclean"))
    out = Path(os.getenv("DIST_DIR", root / "dist"))
    out.mkdir(exist_ok=True)

    for setup_py in glob.glob(str(pq_dir / "**" / "setup.py"), recursive=True):
        pkg_dir = Path(setup_py).parent
        subprocess.run(
            [
                "python",
                "setup.py",
                "bdist_wheel",
                "--plat-name",
                "manylinux_x86_64",
                "--dist-dir",
                str(out),
            ],
            cwd=pkg_dir,
            check=True,
        )


if __name__ == "__main__":  # pragma: no cover
    main()
