# Changelog

## [v0.1-core-ready] – 2025-06-XX

### A. Code Quality & Pre-commit
- Полный pre-commit: ruff, black, isort, mypy.

### B. Supply-Chain Security
- SBOM через Syft, сканирование Grype и Trivy.
- Подпись пакетов Cosign.

### C. DevSecOps & Static Analysis
- CodeQL, Semgrep, Bandit.

### D. Secrets Management
- Интеграция с Vault/AWS SM.

### E. Logging & Monitoring
- secure_logging.py: AES-GCM + TPM ключ.
- self_watchdog: мониторинг хеша и файлов.

### F. File Permissions
- umask 027, chmod 600 на критичных файлах.

### G. Remote Attestation
- tpm2_quote и tpm2_verifysignature при старте.

### H. Documentation & CI/CD
- Полный CI: lint → type-check → tests → security → build/sign.

## [Unreleased]
- Дополнительные fuzz-тесты и периодические сканы SBOM.
