## [vX.0-pseudohsm] – 2025-06-XX
- Интегрирован Quantum-Pseudo-HSM:
  - Добавлены модули device_fp.py, crypto_core.c, shard_secret.py, counter.py, anti_snapshot.py, hardening.c.
  - Полностью удалены зависимости от TPM.
  - Обновлён cli.py: команды enrol/pack/unpack с pseudo-HSM.
  - Добавлены новые тесты: test_device_fp.py, test_crypto_core.py, test_shard_secret.py, test_counter.py, test_anti_snapshot.py, test_cli_pseudohsm.py.
  - CI: сборка C-модулей, новые security-джобы (SBOM-weekly, lint_docs, fuzz_tests).
  - Удалены файлы tpm_attestation.py и упоминания TPM.
