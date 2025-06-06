# Changelog
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
