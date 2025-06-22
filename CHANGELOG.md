# Changelog
## [0.1.0] — 2025-06-07
- Maintenance updates.

## 0.7.1 – CI timeout improvements
- Added `pytest-timeout` dependency and global 5 minute timeout for tests.
- The CI workflow now sets `timeout-minutes: 30` for the pytest step to
  prevent hanging jobs.

## 0.7.0 – PQ-Migration (Stage 5)
- Added `pq_crypto` module with Kyber768 KEM and Dilithium2 signature helpers.
- Introduced `derive_key_pq` for deriving symmetric keys from PQ secrets.
- Implemented `PQAEAD` and extended container format with post-quantum mode.
- CLI commands `gen_kem_keys` and `gen_sig_keys` added with PQ options for `pack` and `unpack`.
- Added comprehensive tests covering PQ modules and CLI.
## 0.6.0 – Anti-rollback, Anti-snapshot, Self-destruct (Stage 4)
- Added counter, anti_snapshot, and recovery modules with tests and CLI commands.


## 0.5.0 – Device Fingerprint (Stage 3)
- Added `device_fp` helpers: `collect_hw_factors` and `compute_fp`.
- Added `zilant fingerprint` CLI command.
- New tests cover device fingerprint utilities and CLI.

## 0.3.0 - Pseudo-HSM Stage 1
- Added hardware fingerprint collection with HMAC.
- Implemented XOR secret sharding and recovery.
- Persistent counter with optional file storage.
- Snapshot detection lock file.
- Updated README with Stage 1 notes.

## 0.4.0 – Secure Container (Stage 2)
- Added simple `.zil` container with metadata and AES-based encryption.
- CLI now supports `pack` and `unpack` commands.
- Introduced integration tests for packing and unpacking files.
## 0.7.2 - 2025-06-07
- Maintenance updates.

## 0.8.0 - 2025-06-22
- Add unified security compliance suite and workflow.
- Enable automated crypto threat model generation.
- Introduce policy enforcement validator with auto-fix helper.
- Document new CI badges in README.
