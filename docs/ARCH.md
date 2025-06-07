# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core Contributors

# Architecture Overview

```mermaid
flowchart TD
    CLI["CLI\n(zilctl)"] --> Core
    Core["Core Library"] --> Logger["Secure Logger"]
    Core --> Vault["Vault/Pseudo‑HSM"]
    Core --> SBOM["SBOM tools"]
```

- **CLI** – user facing commands.
- **Core Library** – cryptography and container logic.
- **Secure Logger** – encrypts audit logs with AES‑GCM.
- **Vault/Pseudo‑HSM** – secrets storage.
- **SBOM tools** – reproducible builds and vulnerability scanning.
