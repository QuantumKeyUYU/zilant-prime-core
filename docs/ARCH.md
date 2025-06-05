# Architecture Overview

```plantuml
@startuml
title Zilant Prime Core Architecture

!define RECTANGLE class

RECTANGLE "CLI\n(zilctl)" as CLI
RECTANGLE "Core Library\n(container, crypto, vdf)" as Core
RECTANGLE "Secure Logger\n(utils/secure_logging.py)" as Logger
RECTANGLE "CI/CD\n(GitHub Actions)" as CICD
RECTANGLE "Vault / TPM\n(secret management)" as Vault
RECTANGLE "SBOM & Scanning\n(syft, grype, trivy)" as SBOM

CLI --> Core : uses
Core --> Logger : logs
CICD --> SBOM : generates and scans
CICD --> Core : builds/tests
CICD --> Vault : fetches secrets & rotates tokens
Vault --> Core : provides AppRole tokens
Vault --> Logger : optional key storage via env
@enduml
