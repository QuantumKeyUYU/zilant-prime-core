# Threat Model

This document summarises security considerations for Zilant Prime Core.

## STRIDE

| Category | What is mitigated | What remains |
|---|---|---|
| Spoofing | TPM based attestation of the build host | Add mutual TLS for CLI connections |
| Tampering | Signed artifacts and SBOM checks | Runtime file integrity monitoring |
| Repudiation | Encrypted structured logs | Central log aggregation |
| Information Disclosure | Secrets stored in Vault, logs encrypted | Periodic key rotation |
| Denial of Service | Self watchdog detects tampering | Rate limiting for CLI operations |
| Elevation of Privilege | Minimal CI permissions | Harden Vault policies |

## MITRE ATT&CK

| ID | Technique | Usage |
|----|-----------|-------|
| T1550 | Use Alternate Authentication Material | Vault AppRole tokens for CI |
| T1486 | Data Encrypted for Impact | Encrypted logs stored locally |
| T1595 | Active Scanning | Automatic SBOM scans in CI |
| T1588 | Obtain Capabilities | Downloading signing keys from Vault |
| T1552 | Unsecured Credentials | Prevented via Vault secret injection |
