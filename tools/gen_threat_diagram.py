import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
OUT = ROOT / "docs" / "threats.mmd"

pattern_class = re.compile(r"class (\w*ThreatModel)")
pattern_annot = re.compile(r"ThreatModel:\s*(\w+)")

nodes = []
for path in SRC.rglob("*.py"):
    text = path.read_text(errors="ignore")
    for m in pattern_class.finditer(text):
        nodes.append(m.group(1))
    for m in pattern_annot.finditer(text):
        nodes.append(m.group(1))

OUT.write_text("flowchart LR\n" + "\n".join(
    [f"  TM{i+1}[\"ThreatModel: {name}\"]" for i, name in enumerate(nodes)] +
    [f"  TM{i} --> TM{i+1}" for i in range(1, len(nodes))]
))
print(OUT)
