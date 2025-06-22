# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

SPHINXBUILD ?= sphinx-build
SPHINXOPTS  ?=
SOURCEDIR   ?= .
BUILDDIR    ?= _build

MERMAID     ?= npx -y @mermaid-js/mermaid-cli@8.9.1
MERMAID_OPTS ?= --no-sandbox
DIAGRAM_SRC  = architecture/key_lifecycle.mmd
DIAGRAM_OUT  = _static/key_lifecycle.svg
export PUPPETEER_DISABLE_SANDBOX ?= true

.PHONY: html clean mermaid

ifeq ($(SKIP_MERMAID),1)
html:
	$(SPHINXBUILD) -M html $(SOURCEDIR) $(BUILDDIR) $(SPHINXOPTS)
else
html: mermaid
	$(SPHINXBUILD) -M html $(SOURCEDIR) $(BUILDDIR) $(SPHINXOPTS)

	mermaid: $(DIAGRAM_OUT)

	$(DIAGRAM_OUT): $(DIAGRAM_SRC)
	$(MERMAID) $(MERMAID_OPTS) -i $< -o $@
endif

clean:
	rm -rf $(BUILDDIR) $(DIAGRAM_OUT)
