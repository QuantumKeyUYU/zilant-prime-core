# Zilant Prime Core

[![Coverage](https://img.shields.io/codecov/c/github/QuantumKeyUYU/zilant-prime-core?branch=main)](https://codecov.io/gh/QuantumKeyUYU/zilant-prime-core)
[![CI](https://github.com/QuantumKeyUYU/zilant-prime-core/actions/workflows/ci.yml/badge.svg)](https://github.com/QuantumKeyUYU/zilant-prime-core/actions/workflows/ci.yml)
[![Quality](https://github.com/QuantumKeyUYU/zilant-prime-core/actions/workflows/quality.yml/badge.svg)](https://github.com/QuantumKeyUYU/zilant-prime-core/actions/workflows/quality.yml)
[![Security Compliance](https://github.com/QuantumKeyUYU/zilant-prime-core/actions/workflows/security-compliance-suite.yml/badge.svg)](https://github.com/QuantumKeyUYU/zilant-prime-core/actions/workflows/security-compliance-suite.yml)
[![Crypto Threat Model](https://github.com/QuantumKeyUYU/zilant-prime-core/actions/workflows/crypto-threat-model.yml/badge.svg)](https://github.com/QuantumKeyUYU/zilant-prime-core/actions/workflows/crypto-threat-model.yml)
[![Python Security](https://github.com/QuantumKeyUYU/zilant-prime-core/actions/workflows/python-security.yml/badge.svg)](https://github.com/QuantumKeyUYU/zilant-prime-core/actions/workflows/python-security.yml)
[![Trivy Critical Scan](https://github.com/QuantumKeyUYU/zilant-prime-core/actions/workflows/trivy-critical-scan.yml/badge.svg)](https://github.com/QuantumKeyUYU/zilant-prime-core/actions/workflows/trivy-critical-scan.yml)
[![SBOM](https://github.com/QuantumKeyUYU/zilant-prime-core/actions/workflows/sbom.yml/badge.svg)](https://github.com/QuantumKeyUYU/zilant-prime-core/actions/workflows/sbom.yml)

Универсальная CLI и библиотека для создания **безопасных контейнеров**, шифрования логов,
VDF-доказательств и построения полной **DevSecOps-цепочки** вокруг криптосредств.

```mermaid
graph LR
  A[Акторы] -->|атакуют| B[CLI]
  B -->|шифрует| C[AEAD Core]
  C --> D[Контейнер]
  C --> E[Watchdog]
  A -->|саботаж| E
  A -->|перехват| F[Журналы]
  F -->|шифруются| G[SecureLogger]
Status / Stages
Stage 0: Secure Logging ✅ (завершено)
Компонент SecureLogger:

Пишет зашифрованные AES-GCM записи в журнал и корректно их расшифровывает.

Защищает от log-injection: ASCII-whitelist + экранирование \n, \r.

Использует singleton-инициализацию через get_secure_logger().

Полный набор тестов (100 % покрытие модуля):

сериализация / десериализация (test_secure_logging*.py);

обработка битых строк и неправильного JSON;

дополнительные поля, валидация типов;

сценарии tampering и пропуска строк.

SPDX-хедеры проставлены в исходниках.

Чеклист Stage 0

 SecureLogger с AES-GCM и read_logs()

 Обработка отсутствия файла, некорректного base64 / JSON

 Экранирование небезопасных символов

 Singleton-логгер (get_secure_logger)

 Тесты на все ветки

 Обновлён README со статусом Stage 0

Stage 1: Quantum-Pseudo-HSM 🧪 (в работе)
Базовые кирпичики офлайн-слоя Pseudo-HSM:

device_fp.py — собирает характеристики железа и строит детерминированный fingerprint устройства.

shard_secret.py — XOR-шардинг секрета.

counter.py — монотонный счётчик в файле.

anti_snapshot.py — lock-файл для детекта снапшотов / откатов.

CLI использует эти примитивы на старте, подготавливая почву для полноценного Pseudo-HSM-режима.

Документация
Threat Model: docs/THREATS.md

Architecture: docs/ARCH.md

Security Policy: SECURITY.md

Установка
Из PyPI (как только пакет станет публичным)
bash
Копировать код
pip install zilant-prime-core
Из исходников (сейчас основной путь)
bash
Копировать код
git clone https://github.com/QuantumKeyUYU/zilant-prime-core.git
cd zilant-prime-core

python -m venv .venv           # или py -m venv .venv на Windows
source .venv/bin/activate      # Windows: .venv\Scripts\Activate.ps1

pip install -e .[dev]          # editable + dev-зависимости
pytest -q                      # быстрый прогон тестов
Quickstart: контейнеры
После установки CLI доступен как zilctl (в CI / Linux) или через python zil.py локально.

Базовый пример
bash
Копировать код
# шифрование файла в контейнер
zilctl pack secret.txt secret.zil

# либо локально из исходников:
python zil.py pack secret.txt secret.zil
C фейковыми данными и метаданными
bash
Копировать код
zilctl pack secret.txt secret.zil \
  --fake-metadata \
  --decoy 2 \
  -p mypass
Интеграция с HashiCorp Vault
Пароль можно брать из Vault (поле password):

bash
Копировать код
export VAULT_ADDR="https://vault.example.com"
export VAULT_TOKEN="s.1a2b3c4d"

zilctl pack secret.txt \
  --vault-path secret/data/zilant/password
Расшифровка
bash
Копировать код
zilctl unpack secret.zil --output-dir ./out
# или локально:
python zil.py unpack secret.zil --output-dir ./out
Honeypot-режим
При неверном пароле отдаётся приманка, а событие уходит в журнал:

bash
Копировать код
zilctl unpack secret.zil -p wrong --honeypot-test
Метаданные и поведение при атаках
Пример сравнения настоящего и фейкового контейнера:

bash
Копировать код
zilctl uyi show-metadata secret.zil
# {"magic":"ZILANT","version":1,"mode":"classic","nonce_hex":"...","orig_size":5,
#  "checksum_hex":"...","owner":"anonymous","timestamp":"1970-01-01T00:00:00Z","origin":"N/A"}

zilctl uyi show-metadata decoy_abcd.zil
# {"magic":"ZILANT","version":1,"mode":"classic","nonce_hex":"...","orig_size":1024,
#  "checksum_hex":"...","owner":"anonymous","timestamp":"1970-01-01T00:00:00Z","origin":"N/A"}
Ожидаемое поведение:

Атака	Результат
Неверный пароль (honeypot)	Создаётся decoy-контейнер, в журнале событие decoy_event
Повреждение контейнера	Ошибка целостности, данные не раскрываются
Массовое вскрытие / bruteforce	Счётчик get_open_attempts отражает все попытки

Anti-Forensics & Real-World Attacks
Decoy-контейнеры помогают запутать форензик-анализ. Флаги:

--decoy — создаёт приманку с псевдо-данными.

--decoy-expire — задаёт TTL, после которого приманка исчезает.

Когда honeypot-режим активен, для неверных паролей возвращается decoy и
логируется decoy_event.

Потенциальные векторы всё ещё остаются:

Побочные каналы по времени / трафику, если decoy не удаляется достаточно быстро.

Корреляция по access-time, если уборка приманок задерживается.

Параллельные атаки
Массовый bruteforce легко заметить по счётчику get_open_attempts:
каждый процесс unpack увеличивает его. Honeypot-ловушки тоже запускаются
параллельно — каждый создаёт свой контейнер-приманку.

Decoy lifecycle & safety FAQ
Decoy-файлы — временные контейнеры-приманки.

При создании с --decoy-expire они исчезают автоматически после задержки.

Если decoy пропал раньше срока, в аудит-журнал пишется событие
decoy_removed_early.

При плановой очистке (авто или ручной) добавляется decoy_purged.

Ручная очистка:

bash
Копировать код
zilctl --decoy-sweep
zilctl --decoy-sweep --paranoid   # дополнительно выводит, сколько приманок удалено
Shamir Secret Sharing
Разделите мастер-ключ на части и восстановите его при необходимости:

bash
Копировать код
zilctl key shard export \
    --master-key cosign.key \
    --threshold 3 \
    --shares 5 \
    --output-dir shards
Храните shards/share*.hex и shards/meta.json в разных безопасных местах.

Восстановление:

bash
Копировать код
zilctl key shard import \
    --input-dir shards \
    --output-file master.key
Для восстановления достаточно собрать threshold частей в одной директории.

Stream Verification
Проверка целостности большого контейнера без распаковки:

bash
Копировать код
zilctl stream verify big.zst --key master.key
Проверка заголовка контейнера:

bash
Копировать код
zilctl uyi verify-integrity secret.zil
zilctl uyi show-metadata secret.zil
Изменение хотя бы одного байта приводит к ошибке «MAC mismatch».

HPKE Encryption
Гибридное шифрование (Kyber768 + X25519) доступно через подкоманды hpke:

bash
Копировать код
zilctl hpke encrypt src.bin ct.bin \
    --pq-pub kyber.pk \
    --x-pub x25519.pk

zilctl hpke decrypt ct.bin out.bin \
    --pq-sk kyber.sk \
    --x-sk x25519.sk
Root Baseline
Zilant Prime Core останавливает выполнение, если обнаружены признаки root / отладки.

Проверяется (на уровне импорта модуля):

UID / GID равен нулю;

типичные пути su / Magisk;

корневая ФС примонтирована как rw;

SELinux выключен или в permissive;

активный трейс по /proc/self/status.

В этом случае процесс завершается с кодом 99.

Для тестирования можно явно разрешить root:

bash
Копировать код
export ZILANT_ALLOW_ROOT=1
python -c "import zilant_prime_core"
harden_linux() можно дернуть вручную:

bash
Копировать код
python - <<'EOF'
import zilant_prime_core

zilant_prime_core.harden_linux()
print("hardened")
EOF
Migration guide
python
Копировать код
from zilant_prime_core.utils import pq_crypto

kem = pq_crypto.HybridKEM()
pk_pq, sk_pq, pk_x, sk_x = kem.generate_keypair()
ct_pq, _ss_pq, epk, _ss_x, shared = kem.encapsulate((pk_pq, pk_x))
ss = kem.decapsulate((sk_pq, sk_x), (ct_pq, epk, b""))
CLI-флоу регистрации и логина через OPAQUE:

bash
Копировать код
zilctl register --server https://auth.example --username alice
zilctl login    --server https://auth.example --username alice
Development
Локальная разработка
bash
Копировать код
git clone https://github.com/QuantumKeyUYU/zilant-prime-core.git
cd zilant-prime-core

python -m venv .venv           # Windows: py -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\Activate.ps1

pip install -e .[dev]
pytest -q
На Windows специфичные тесты (fuse, VDF, PQ-крипта) помечены как SKIPPED —
это ожидаемое поведение, CI их прогоняет на Linux.

Code Owners & Static Analysis
Код и тесты поддерживаются @QuantumKeyUYU.

CI-воркфлоу покрывают:

ruff, mypy, bandit, semgrep;

CodeQL-анализ;

Trivy-скан контейнера;

генерацию SBOM.

Semgrep использует кастомные правила из .semgrep для предотвращения:

захардкоженных ключей;

небезопасного random / hashlib;

открытых файлов без with.

Security Checks
Автоматически собираются артефакты:

Unified compliance report — security_compliance_report.md

Crypto threat report — crypto_threat_report.md

Policy enforcement report — policy_report.md

(пути и формат могут меняться по мере развития проекта).

Roadmap / TODO Stage III
GUI-демо (PyQt / Web).

Bug bounty-политика и обновлённый SECURITY.md.

Docker-образ с безопасным entrypoint:

bash
Копировать код
docker run --rm ghcr.io/quantumkeyuyu/zilant-prime-core \
  python -c "import zilant_prime_core; zilant_prime_core.harden_linux()"
Zilant Prime Core задуман как «криптографический швейцарский нож» с DevSecOps-поясом:
от безопасных логов и контейнеров — до VDF и пост-квантовых протоколов.
