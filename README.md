# Zilant Prime Core

[![Coverage](https://img.shields.io/codecov/c/github/QuantumKeyUYU/zilant-prime-core?branch=main)](https://codecov.io/gh/QuantumKeyUYU/zilant-prime-core) [![Security](https://img.shields.io/badge/security-scan-passed-success.svg)](https://github.com/QuantumKeyUYU/zilant-prime-core/security) [![Docs](https://img.shields.io/badge/docs-available-blue.svg)](./docs/ARCH.md)

Универсальная CLI и библиотека для создания безопасных контейнеров, шифрования логов, VDF-доказательств и полной DevSecOps-цепочки.

---

## Stage 0: Secure Logging (завершено)

В этом этапе мы реализовали и протестировали компонент **SecureLogger**:

- Код записывает зашифрованные AES-GCM записи в файл и корректно их расшифровывает.
- Обработка log-injection через фильтрацию ASCII-символов и экранирование `\n`, `\r`.
- Singleton-логирование через `get_secure_logger()`.
- Полный набор тестов (100 % покрытие):
  - Проверка сериализации/десериализации (`test_secure_logging.py`).
  - Обработка некорректных строк и JSON.
  - Дополнительные поля, валидация типа ключа.
  - Сценарии tampering и пропуска битых строк.
- **SPDX-блок** добавлен в каждый файл.

### Чеклист по Secure Logging:
- [x] `SecureLogger` с AES-GCM и `read_logs()`.
- [x] Обработка отсутствия файла, некорректного base64, JSON.
- [x] Экранирование небезопасных символов.
- [x] Singleton-логгер (`get_secure_logger`).
- [x] Тесты на все ветки (`test_secure_logging*.py`).
- [x] README обновлён, добавлен статус Stage 0.

---

## Этап 1: Crystal Update

Новые возможности:

- `--decoy-size` (маскировка размера payload)
- Sandbox-wrapper (`runsc`)
- TPM counter (fail-closed)
- Rate Limiting + Suspicion Logging
- Unpack jitter и вывод Canary JSON
- Constant-time сравнения (`bytes_equal_ct`)
- Self-watchdog с перекрёстной проверкой

Примеры команд:

```bash
zilant pack file.txt -p <пароль> --decoy-size 1024
zilant unpack container.zil -p <пароль>
```

---

## Документация

- **Threat Model**: [docs/THREATS.md](docs/THREATS.md)
- **Architecture**: [docs/ARCH.md](docs/ARCH.md)

---

## Quickstart

```bash
pip install zilant-prime-core

# Шифрование файла:
zilctl pack secret.txt secret.zil

# Расшифровка:
zilctl unpack secret.zil --output-dir ./out

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pre-commit run --all-files
ruff check src tests
black --check src tests
mypy src
pytest
python -m build
```

## Local Testing

On Unix-like systems run:

```bash
./scripts/test_local.sh
```

On Windows PowerShell:

```powershell
./scripts/test_win.ps1
```

Signed artifacts can be produced via CI or locally using `cosign sign` with your key. After installation run `scripts/post_install.sh` to enforce permissions.

## Vault integration
Чтобы подключить Vault в будущем, добавьте шаг в CI:
```yaml
- name: Fetch secrets from Vault
  uses: hashicorp/vault-action@v2
  with:
    url: ${{ secrets.VAULT_URL }}
    method: github
    path: secret/data/zilant
    token: ${{ secrets.VAULT_TOKEN }}
```
И настройте `secrets.VAULT_URL` и `secrets.VAULT_TOKEN` в репозитории.
