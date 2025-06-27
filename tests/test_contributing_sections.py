# tests/test_contributing_sections.py

from pathlib import Path


def test_contributing_sections():
    text = Path("CONTRIBUTING.md").read_text(encoding="utf-8")
    required = [
        "# Contributing to Zilant Prime Core",
        "## Linting",
        "## Testing",
        "## Commits",
    ]
    for section in required:
        assert section in text, f"Section not found: {section}"
