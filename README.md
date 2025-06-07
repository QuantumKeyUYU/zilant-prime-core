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

## Stage 1: Quantum‑Pseudo‑HSM (в работе)

В рамках первого этапа интеграции офлайн‑слоя Pseudo‑HSM были добавлены базовые
модули:

- `device_fp.py` собирает аппаратные характеристики и формирует детерминированный
  отпечаток устройства.
- `shard_secret.py` реализует XOR‑шардинг секрета.
- `counter.py` хранит монотонный счётчик в файле.
- `anti_snapshot.py` создаёт lock‑файл для обнаружения отката/снапшота.

CLI использует эти функции при старте, что закладывает фундамент для дальнейшей
работы Pseudo‑HSM.

---

## Документация

- **Threat Model**: [docs/THREATS.md](docs/THREATS.md)
- **Architecture**: [docs/ARCH.md](docs/ARCH.md)

---

## Установка

```bash
pip install zilant-prime-core

# опционально: автодополнение
source completions/zilant.bash  # bash
```

---

## Quickstart

```bash
pip install zilant-prime-core

# Шифрование файла:
zilctl pack secret.txt secret.zil

# Или через HashiCorp Vault (поле `password`):
export VAULT_ADDR="https://vault.example.com"
export VAULT_TOKEN="s.1a2b3c4d"
zilctl pack secret.txt --vault-path secret/data/zilant/password

# Расшифровка:
zilctl unpack secret.zil --output-dir ./out
