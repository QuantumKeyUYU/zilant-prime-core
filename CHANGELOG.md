# Changelog

## [Unreleased]
- Добавлена опция --decoy-size (padding payload)
- Реализован Sandbox Runner через runsc
- Введён RateLimiter (5 вызовов/мин) и Suspicion Logging
- При распаковке добавлен jitter и вывод Canary JSON
- Написана constant-time функция bytes_equal_ct и заменены сравнения подписи
- Расширен self-watchdog – cross-verification родитель↔дочерний
- Написаны unit-тесты для всех новых модулей

## [v0.1-core-ready] – 2025-06-XX
### A. Code Quality
- Обновлены конфигурации линтеров (`ruff.lint.ignore` и т.д.), все ошибки исправлены.
- Файл `update_all_exports.py` удалён.
- 100 % покрытие тестами, CI green.

### B. SBOM & Supply-Chain
- Добавлен Syft (sbom.json), Grype (--fail-on medium), Trivy (--severity HIGH,CRITICAL).
- Cosign подписи артефактов.

### C. DevSecOps
- CodeQL, Semgrep включены в CI без ошибок.
- secure_logging (AES-GCM).

### D. Документация
- THREATS.md и ARCH.md авто-генерируются и проходят remark.
