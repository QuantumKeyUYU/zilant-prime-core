# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

# ----------------------- paths / tools -----------------------------
SPHINXBUILD   ?= sphinx-build
SPHINXOPTS    ?=
SOURCEDIR     ?= .
BUILDDIR      ?= _build

MERMAID       ?= npx -y @mermaid-js/mermaid-cli@8.9.1
MERMAID_OPTS  ?= --no-sandbox
DIAGRAM_SRC    = architecture/key_lifecycle.mmd
DIAGRAM_OUT    = _static/key_lifecycle.svg
export PUPPETEER_DISABLE_SANDBOX ?= true

.PHONY: help clean mermaid html

help:
	@echo "make mermaid   – обновить все *.mmd → SVG"
	@echo "make html      – полная сборка HTML (вызывает mermaid)"
	@echo "make clean     – стереть $(BUILDDIR) и сгенерённые SVG"

# ----------------------- mermaid diagrams --------------------------
$(DIAGRAM_OUT): $(DIAGRAM_SRC)
	$(MERMAID) $(MERMAID_OPTS) -i $< -o $@

mermaid: $(DIAGRAM_OUT)

# ----------------------- Sphinx build ------------------------------
html: mermaid
	# -W: treat warnings as errors
	$(SPHINXBUILD) -M html $(SOURCEDIR) $(BUILDDIR) "-W $(SPHINXOPTS)"

clean:
	rm -rf $(BUILDDIR) $(DIAGRAM_OUT)
