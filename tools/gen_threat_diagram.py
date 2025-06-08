#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core Contributors
"""Generate a simple Mermaid diagram from docs/THREATS.md."""
from __future__ import annotations

import re
from pathlib import Path

THREATS_MD = Path("docs/THREATS.md")
DIAGRAM_MMD = Path("docs/threats_diagram.mmd")


def parse_adversaries(text: str) -> list[tuple[str, str]]:
    pat = re.compile(r"- \*\*(A\d+) – ([^*]+)\*\*")
    return pat.findall(text)


def main() -> None:
    content = THREATS_MD.read_text()
    start = content.find("## Adversaries")
    end = content.find("##", start + 1)
    section = content[start:end] if start != -1 and end != -1 else ""
    adversaries = parse_adversaries(section)

    lines = ["graph TD", "  Core[Zilant Core]"]
    for code, name in adversaries:
        safe_name = name.strip().replace("\n", " ")
        lines.append(f"  {code}([{safe_name}]) --> Core")

    DIAGRAM_MMD.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
