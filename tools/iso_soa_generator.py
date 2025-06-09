#!/usr/bin/env python3
"""
Генерирует SoA ISO 27001 в Markdown на основе простого YAML‑списка контролей.
YAML по умолчанию лежит в docs/iso_controls.yml (можно переопределить аргументом).
"""

from __future__ import annotations

import sys
from pathlib import Path
from textwrap import indent

import yaml

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("docs/iso_controls.yml")
DST = Path("docs/SoA_ISO27001.md")

if not SRC.exists():
    sys.exit(f"❌  source controls file {SRC} not found")

controls: list[dict[str, str]] = yaml.safe_load(SRC.read_text())
lines = ["# Statement of Applicability (ISO 27001:2022)\n"]
for ctrl in controls:
    lines.append(f"## {ctrl['id']} — {ctrl['name']}\n")
    rationale = ctrl.get("rationale", "—")
    lines.append("**Rationale**\n\n" + indent(rationale, "    ") + "\n")
DST.write_text("\n".join(lines))
print("✅  SoA saved →", DST)
