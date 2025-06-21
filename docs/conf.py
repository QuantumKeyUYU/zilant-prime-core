# docs/conf.py
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core Contributors

import os
import sys

# Чтобы Sphinx видел пакет
sys.path.insert(0, os.path.abspath("../src"))
os.environ.setdefault("ZILANT_ALLOW_ROOT", "1")

# -- Project information -----------------------------------------------------

project = "Zilant Prime Core"
author = "Zilant Prime Core Contributors"
release = "0.1.0"

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx_autodoc_typehints",
    "m2r2",
    "sphinxcontrib.mermaid",
]

# Автоматически генерить заглушки для модулей
autosummary_generate = True

# Опции по умолчанию для autodoc
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# Mermaid (если нужна встроенная диаграмма)
mermaid_cmd = "npx -y @mermaid-js/mermaid-cli --no-sandbox"
mermaid_output_format = "png"

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- HTML output -------------------------------------------------------------

html_theme = "alabaster"
html_static_path = ["_static"]
