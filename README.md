# Zilant Prime Core

[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)](https://codecov.io/gh/QuantumKeyUYU/zilant-prime-core)
[![CI](https://img.shields.io/badge/ci-passing-brightgreen)](https://github.com/QuantumKeyUYU/zilant-prime-core/actions)
[![Security](https://img.shields.io/badge/security-passed-brightgreen)](https://github.com/QuantumKeyUYU/zilant-prime-core/security)
[![Reproducible](https://img.shields.io/badge/reproducible-yes-blue)](https://github.com/QuantumKeyUYU/zilant-prime-core)

Universal CLI and library for encrypted containers and full DevSecOps pipeline.

## Installation

```bash
pip install zilant-prime-core
```

## Linters and tests

```bash
pre-commit run --all-files
pytest --cov=zilant_prime_core
```

## Build & sign

```bash
python -m build --sdist --wheel
cosign sign --key cosign.key dist/*
```

## Vault secrets

```bash
vault login <root-token>
vault kv put secret/ci \
    COSIGN_KEY_B64="<base64-ключ>" \
    PYPI_API_TOKEN="<PyPI-токен>"
```

TPM integration is used when available for sealing log keys and for remote attestation.

To regenerate the architecture diagram:

```bash
plantuml docs/ARCH.puml -o docs
```
