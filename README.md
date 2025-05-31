# Zilant Prime Core

[![Coverage](https://img.shields.io/codecov/c/github/QuantumKeyUYU/zilant-prime-core?branch=main)](https://codecov.io/gh/QuantumKeyUYU/zilant-prime-core) [![Security](https://img.shields.io/badge/security-scan-passed-success.svg)](https://github.com/QuantumKeyUYU/zilant-prime-core/security) [![Docs](https://img.shields.io/badge/docs-available-blue.svg)](./docs/ARCH.md)

Универсальная CLI и библиотека для создания безопасных контейнеров, шифрования логов, VDF-доказательств и полной DevSecOps-цепочки.

---

## Документация

- **Threat Model**: [docs/THREATS.md](docs/THREATS.md)  
- **Architecture**: [docs/ARCH.md](docs/ARCH.md)  

---

## Quickstart

```bash
pip install zilant-prime-core

# Зашифровать файл
zilctl pack secret.txt secret.zil

# Расшифровать
zilctl unpack secret.zil --output-dir ./out
