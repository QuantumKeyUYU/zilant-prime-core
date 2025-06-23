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
## 0.8.1 - 2025-06-22
- Ensure generated reports end with a newline for pre-commit compliance.

## 0.8.2 - 2025-06-23
- Added `--fake-metadata` and `--decoy` options for `pack`.
- Introduced honeypot test mode for `unpack` with decoy output.
- New commands `uyi verify-integrity` and `uyi show-metadata`.
- Container unpack attempts are now tracked via `get_open_attempts`.
- Documentation updated with new examples.

## 0.8.3 - 2025-06-23
- Decoy files are now full `.zil` containers for better realism.
- Integrity verification extended to damaged decoys and race conditions.
- Added `tests/test_decoy_vs_real.py` covering honeypot edge cases.
- README documents attack scenarios and metadata comparison.

## 0.8.4 - 2025-06-24
- Added `--decoy-expire` option to auto-delete bait containers.
- Honeypot traps support concurrent triggers and cleanup.
- New smoke tests ensure decoy and real containers share identical metadata.
- README now features anti-forensics guidance and brute-force countermeasures.

## 0.8.5 - 2025-06-25
- Log decoy purging and early removals via the audit ledger.
- CLI has `--decoy-sweep` and `--paranoid` options with automatic sweeps.
- `sweep_expired_decoys` utility cleans up stale bait files.
- Property-based fuzz tests verify pack/unpack stability.
- README includes "Decoy lifecycle & safety FAQ".
