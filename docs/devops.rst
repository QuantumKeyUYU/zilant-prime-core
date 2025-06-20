.. _devops:

DevOps Guide
============

.. contents:: Contents
   :local:

GUI build
---------

The project provides a small PyQt5 interface. The ``ui-build`` GitHub Actions
workflow uses PyInstaller to produce ``zilant-gui.exe``. To build locally:

.. code-block:: bash

   pip install -e .[ui]
   pyinstaller --onefile --windowed ui/main.py --name zilant-gui

Metrics export
--------------

Run internal metrics via:

.. code-block:: bash

   zilant metrics serve --endpoint http://localhost:4317

SBOM scanning
-------------

The workflow ``sbom-cve.yml`` demonstrates generating a Software Bill of Materials
and running a vulnerability scan with ``grype``. You can reproduce locally:

.. code-block:: bash

   make sbom
   make cve-scan

CodeQL analysis
---------------

The ``codeql-analysis.yml`` workflow executes GitHub's CodeQL security scan
on every push. Trigger it manually or push a branch to run the full analysis.

Security audit
--------------

Review ``docs/QA_CHECK.md`` for the checklist ensuring that linters, tests,
Semgrep and CodeQL reports are all green before release.
