Threat Model
============

Adversaries
-----------

- **A1 – Insider developer**: contributor with repository access who may inject malicious code.
- **A2 – Compromised CI/CD**: attacker gaining control over the automation pipeline.
- **A3 – Stolen cosign keys**: leaked signing material or Vault tokens used outside the organisation.
- **A4 – Malicious dependency**: third‑party package or tool shipping vulnerable code.
- **A5 – Tampering user**: someone modifying artefacts or logs after build.

Security objectives
-------------------

- **C1 – Code integrity**: prevent unauthorised changes to the source.
- **C2 – Traceable logs via audit.log Merkle proofs**: detect tampering after release.
- **C3 – Confidentiality of secrets**: keep Vault tokens and cosign keys encrypted.
- **C4 – Reproducibility**: anyone can rebuild identical artefacts from the same tag.
- **C5 – Vulnerability free**: ship images that pass SBOM scanning.

Asset / Threat / Control
------------------------

.. list-table::
   :header-rows: 1

   * - Asset
     - Threat
     - Control
   * - Source code
     - A1, A2
     - signed commits, CI lint & tests
   * - Secrets
     - A3
     - Vault AppRole, encrypted logs
   * - Dependencies
     - A4
     - SBOM with grype scans
   * - Artefacts
     - A5
     - reproducible build, cosign signatures
   * - Logs
     - A5
     - C2: Merkle-chained ``audit.log`` with AES-GCM SecureLogger

Controls
--------

.. mermaid::

   flowchart TD
       Root --> Container
       Container --> Session
       Session --> Destroy

To export a PNG fallback of the diagram, run::

   npx mmdc -i docs/architecture/key_lifecycle.mmd -o docs/_static/key_lifecycle.png

Then add ``docs/_static/key_lifecycle.png`` to version control if required.
