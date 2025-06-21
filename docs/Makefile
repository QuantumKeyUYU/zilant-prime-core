# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core Contributors

SHELL := /usr/bin/env bash

.PHONY: mermaid html clean

# --------------------------------------------------------------------
# 1) Generate the static SVG once from Mermaid source
# --------------------------------------------------------------------
mermaid: docs/_static/key_lifecycle.svg docs/_static/threat_diagram.svg

docs/_static/key_lifecycle.svg: docs/architecture/key_lifecycle.mmd
	mmdc -i $< -o $@

docs/_static/threat_diagram.svg: docs/threats.mmd
	mmdc -i $< -o $@

# --------------------------------------------------------------------
# 2) Build HTML documentation
# --------------------------------------------------------------------
html: mermaid
	sphinx-build -b html . _build/html

# Convenience target for CI
docs: html

clean:
	rm -rf _build docs/_static/key_lifecycle.svg docs/_static/threat_diagram.svg
