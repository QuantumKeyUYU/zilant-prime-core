# Zilant Prime Core

[![CI](https://github.com/QuantumKeyUYU/zilant-prime-core/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/QuantumKeyUYU/zilant-prime-core/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/codecov/c/github/QuantumKeyUYU/zilant-prime-core?branch=main)](https://codecov.io/gh/QuantumKeyUYU/zilant-prime-core)
[![Docker Scan](https://github.com/QuantumKeyUYU/zilant-prime-core/actions/workflows/trivy-critical-scan.yml/badge.svg?branch=main)](https://github.com/QuantumKeyUYU/zilant-prime-core/actions/workflows/trivy-critical-scan.yml)
[![Docs](https://img.shields.io/badge/docs-online-blue.svg)](https://quantumkeyuyu.github.io/zilant-prime-core/)
![ISO 27001](https://img.shields.io/badge/ISO27001-compliant-brightgreen.svg)

Универсальная CLI и библиотека для создания безопасных контейнеров, шифрования логов, VDF-доказательств и полной DevSecOps-цепочки.

<div class="mermaid">
graph LR
  A[Акторы] -->|атакуют| B[CLI]
  B -->|шифрует| C[AEAD Core]
  C --> D[Контейнер]
  C --> E[Watchdog]
  A -->|саботаж| E
  A -->|перехват| F[Журналы]
  F -->|шифруются| G[SecureLogger]
</div>

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

### Pseudo-HSM CLI

- **init**
  `zilctl hsm init`
  Инициализирует Pseudo-HSM: создаёт `lock.json` и `counter.txt`.

- **seal**
```bash
zilctl hsm seal \
  --master-key master.key \
  --threshold 2 \
  --shares 3 \
  --output-dir shards
```
Генерирует 3 шард-файла `shard_1.hex` … `shard_3.hex` из мастер-ключа.

- **unseal**
```bash
zilctl hsm unseal \
  --input-dir shards \
  --output-file master_restored.key
```
Восстанавливает мастер-ключ из сохранённых шардов.

- **status**
```bash
zilctl hsm status
```
Выводит JSON с полями `created` (timestamp) и `counter`.

#### Quickstart
```bash
# Инициализация
zilctl hsm init

# Разбиваем ключ
zilctl hsm seal --master-key master.key --threshold 2 --shares 3 --output-dir shards

# Восстанавливаем
zilctl hsm unseal --input-dir shards --output-file master_restored.key

# Проверяем статус
zilctl hsm status
# Регистрация
zilctl auth register --server https://auth.example.com --username alice

# Вход
zilctl auth login    --server https://auth.example.com --username alice
```

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

# Просмотр метаданных:
zilctl inspect secret.zil --output json

### Shamir Secret Sharing

Разделите мастер‑ключ на части и восстановите его при необходимости:

```bash
zilctl key shard export --master-key cosign.key \
    --threshold 3 --shares 5 --output-dir shards

# храните файлы shards/share*.hex и shards/meta.json в разных безопасных местах

zilctl key shard import --input-dir shards --output-file master.key
```

Храните полученные шард‑бэкапы на отдельных офлайн‑носителях. Для восстановления
достаточно собрать ``threshold`` частей в одной директории и выполнить команду
``shard import``.

### Stream Verification

Проверить целостность большого контейнера можно без распаковки:

```bash
zilctl stream verify big.zst --key master.key
```

Изменение хотя бы одного байта приведёт к ошибке «MAC mismatch».

### HPKE Encryption

Гибридное шифрование (Kyber768+X25519) доступно через подкоманды ``hpke``:

```bash
zilctl hpke encrypt src.bin ct.bin --pq-pub kyber.pk --x-pub x25519.pk
zilctl hpke decrypt ct.bin out.bin --pq-sk kyber.sk --x-sk x25519.sk
```

### PQ Signatures

```bash
# Генерация PQ-ключей
zilctl pq gen-key --out keys

# Подпись контейнера
zilctl pq sign my.zil --key keys/pq_priv.key

# Проверка подписи
zilctl pq verify my.zil --sig my.zil.sig --key keys/pq_pub.key
```

### OPAQUE Auth

```bash
# Регистрация
zilctl auth register alice

# Вход
zilctl auth login alice
```

## Root Baseline

Zilant Prime Core aborts execution when root or debugging indicators are found.
The following checks are performed at import time:

- UID or GID equals zero
- Typical ``su``/Magisk paths exist
- Root filesystem is mounted writable
- SELinux enforcement disabled
- Active tracer via ``/proc/self/status``

If triggered, the process terminates with exit code ``99``.

## Breaking changes

- Root detection now executes on import and can be bypassed via `ZILANT_ALLOW_ROOT`.
- The PQ-crypto helpers were refactored; import paths may differ.

Example bypass for testing:

```bash
export ZILANT_ALLOW_ROOT=1
python -c "import zilant_prime_core"
```

`harden_linux()` prints nothing on success. You can call it explicitly:

```bash
python - <<'EOF'
import zilant_prime_core

zilant_prime_core.harden_linux()
print("hardened")
EOF
```

## Migration guide

````python
from zilant_prime_core.utils import pq_crypto

kem = pq_crypto.HybridKEM()
pk_pq, sk_pq, pk_x, sk_x = kem.generate_keypair()
ct_pq, _ss_pq, epk, _ss_x, shared = kem.encapsulate((pk_pq, pk_x))
ss = kem.decapsulate((sk_pq, sk_x), (ct_pq, epk, b""))
````

CLI registration and login via OPAQUE:

```bash
zilctl register --server https://auth.example --username alice
zilctl login --server https://auth.example --username alice
```

## Development

### Code Owners & Static Analysis

Source and tests are maintained by @QuantumKeyUYU, while documentation also lists @DocMaintainers. CI workflows fall under @DevSecOpsTeam. Pull requests run Semgrep with custom rules in `.semgrep.yml` to prevent hardcoded keys and insecure random usage.

## Quantum Anonymity & Security

Experimental modules showcasing quantum resistant techniques can be found in
`docs/ANONYMITY.md` and `docs/QUANTUM_SECURITY.md`.
Below is a short example:

```python
from pathlib import Path
from zilant_prime_core.utils import QAL, QSSA, QuantumRA, QVPN, ZKQP

qal = QAL(3, Path('/tmp/qal'))
sig = qal.sign(b'hi', 0)
pubs = [p.read_bytes() for _, p in qal.keys]
assert qal.verify(b'hi', sig, pubs)

qssa = QSSA()
public, private = qssa.generate_keypair()

ra = QuantumRA(Path('/tmp/ra'))
att = ra.attest(b'device')
ra.verify(b'device', att)

vpn = QVPN()
vpn.enable()
vpn.disable()

zk = ZKQP(Path('/tmp/zk'))
commit, proof = zk.prove(b'data')
```

## Documentation

Documentation is automatically published to [GitHub Pages](https://quantumkeyuyu.github.io/zilant-prime-core/).
To build it locally run:

```bash
make -C docs html
```
The output will be available in `docs/_build/html/index.html`.

## TODO Stage III

- GUI demonstration (PyQt/Web)
- Bug bounty policy updates and SECURITY.md
- Docker image with `ENTRYPOINT=python -c "import zilant_prime_core; zilant_prime_core.harden_linux()"`
