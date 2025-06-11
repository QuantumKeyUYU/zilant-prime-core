import re
import sys
from pathlib import Path


def main(src_dir: str | None = None, out_file: str | None = None) -> str:
    root = Path(__file__).resolve().parent.parent
    src = Path(src_dir) if src_dir else root / "src"
    out = Path(out_file) if out_file else root / "docs" / "threats.mmd"

    pattern_class = re.compile(r"class (\w*ThreatModel)")
    pattern_annot = re.compile(r"ThreatModel:\s*(\w+)")

    nodes: list[str] = []
    for path in src.rglob("*.py"):
        text = path.read_text(errors="ignore")
        for m in pattern_class.finditer(text):
            nodes.append(m.group(1))
        for m in pattern_annot.finditer(text):
            nodes.append(m.group(1))

    out.write_text(
        "flowchart LR\n"
        + "\n".join(
            [f'  TM{i+1}["ThreatModel: {name}"]' for i, name in enumerate(nodes)]
            + [f"  TM{i} --> TM{i+1}" for i in range(1, len(nodes))]
        )
    )
    print(out)
    return str(out)


if __name__ == "__main__":  # pragma: no cover
    src = sys.argv[1] if len(sys.argv) > 1 else None
    out = sys.argv[2] if len(sys.argv) > 2 else None
    main(src, out)
