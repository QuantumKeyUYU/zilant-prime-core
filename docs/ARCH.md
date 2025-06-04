# ARCH.md

```plantuml
@startuml
title ZILANT Prime Stage 1 Architecture

rectangle "Git Repo (zilant-prime-core)" as Repo
rectangle "CI/CD (GitHub Actions)" as CI
rectangle "SBOM (Syft → sbom.json)" as Syft
rectangle "Vulnerability Scans (Grype, Trivy)" as Vuln
rectangle "Static Analysis (Bandit, Semgrep, CodeQL)" as Static
rectangle "Build + Sign (python –m build, Cosign)" as BuildSign
rectangle "Monitoring (self-hash, watchdog)" as Monitor
rectangle "Logging (secure_logging, TPM-stub)" as Logging
rectangle "Vault / Secrets" as Vault
rectangle "TPM / Attestation" as TPM
rectangle "Sandbox Runner\n(runsc)" as Sandbox
rectangle "TPM Counter\n(fail-closed)" as TpmCounter
rectangle "RateLimiter +\nSuspicion Logging" as RateSusp
rectangle "Unpack Jitter +\nCanary JSON" as UnpackJitter
rectangle "Self-watchdog\n(Parent↔Child)" as CrossWatchdog

Repo --> CI
CI --> Syft
Syft --> Vuln
CI --> Static
CI --> BuildSign
BuildSign --> [Artifacts]
Repo --> Logging
Logging --> TPM
Repo --> Vault
CI --> Vault
Repo --> Monitor
CI --> Monitor
CLI --> Sandbox
Sandbox --> TpmCounter
TpmCounter --> RateSusp
RateSusp --> Pack/Unpack
Pack/Unpack --> UnpackJitter
Pack/Unpack --> CrossWatchdog
@enduml
```
