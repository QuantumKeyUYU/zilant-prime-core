import json
import os
from pathlib import Path

from jinja2 import Environment, select_autoescape

ROOT = Path(__file__).resolve().parent.parent
tmpl_path = ROOT / "docs" / "SoA_ISO27001.j2"
env = Environment(autoescape=select_autoescape())
with open(tmpl_path) as fh:
    tmpl = env.from_string(fh.read())

with open(ROOT / "docs" / "iso_soa.json") as fh:
    data = json.load(fh)

out = tmpl.render(controls=data["controls"])
output = ROOT / "docs" / "SoA_ISO27001.md"
os.makedirs(output.parent, exist_ok=True)
with open(output, "w") as f:
    f.write(out)
print("SoA ISO27001 generated")
