# Changelog

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
