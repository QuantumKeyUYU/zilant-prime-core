# THREATS.md

## Spoofing (Подделка)
- Пример: злоумышленник пытается выдать себя за CI-агент и подменяет результаты билдов.
- Mitigation: Cosign подписи, Vault-секреты в GitHub Secrets

## Tampering (Подмена)
- Пример: sbom.json изменён вручную после генерации.
- Mitigation: umask 027, inotify/watchdog, HMAC sbom.json

## Repudiation (Отказ от действий)
- Пример: отсутствие аудита действий при сборке.
- Mitigation: защищённые журналы с AES-GCM, TPM-ключ.

## Information Disclosure (Разглашение)
- Пример: утечка ключей Cosign или секретов Vault.
- Mitigation: шифрование логов, ограниченные права доступа.

## Denial of Service (Отказ в обслуживании)
- Пример: DoS на CI/CD через нагрузку фазового VDF.
- Mitigation: лимиты ресурсов и мониторинг watchdog.

## Elevation of Privilege (Повышение привилегий)
- Пример: использование скомпрометированных токенов для подписи.
- Mitigation: двухфакторная подпись, аттестация TPM.

## MITRE ATT&CK
- T1552.001 (Credentials in Secret) → Mitigation: Vault + ротация
- T1588 (Obtain Resources) → Mitigation: ограниченные токены, IAM
- T1499 (Resource Hijacking/DoS) → Mitigation: лимиты ресурсов
