# Threat Model

Этот документ описывает угрозы для Zilant Prime Core по методикам STRIDE и MITRE ATT&CK.

## STRIDE

| Категория           | Угроза                                                                 |
|---------------------|------------------------------------------------------------------------|
| **Spoofing**        | Подмена ключей (Vault AppRole, TPM); фейковые сервисы CI/CD            |
| **Tampering**       | Модификация SBOM, логов или скомпилированных артефактов                |
| **Repudiation**     | Отсутствие следов операций (логов), отсутствие подписи артефактов      |
| **Information Disclosure** | Утечка логов (без шифрования), секретов из CI/CD или TPM             |
| **Denial of Service** | Отказ в обслуживании CI (удаление workflow), истощение ресурсов KDF     |
| **Elevation of Privilege** | Неавторизованная подпись через Cosign, привилегии Vault-токенов        |

## MITRE ATT&CK

| ID       | Technique                          | Пример                                |
|----------|------------------------------------|---------------------------------------|
| T1550    | Use Alternate Authentication Material | Кража AppRole SecretID                |
| T1486    | Data Encrypted for Impact          | Шифрование логов без хранения ключа   |
| T1595    | Active Scanning                    | Автоматические SBOM-сканы в CI        |
| T1588    | Obtain Capabilities                | Загрузка ключей Cosign из Secrets     |
| T1552    | Unsecured Credentials              | Хранение паролей в переменных среды   |
