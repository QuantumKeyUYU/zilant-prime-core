# Zilant Prime Core

Quantum-Pseudo-HSM integration providing secure container operations.

## Quantum-Pseudo-HSM

This release introduces a pseudo-HSM layer with device fingerprinting and secure key derivation.

### Commands

```bash
zilant enrol myshard.bin
zilant pack myshard.bin secret.txt secret.zil
zilant unpack myshard.bin secret.zil restored.txt
```

Compile C modules:

```bash
gcc -fPIC -shared src/zilant_prime_core/utils/crypto_core.c -o src/zilant_prime_core/utils/crypto_core.so -lcrypto
gcc -fPIC -shared src/zilant_prime_core/utils/hardening.c -o src/zilant_prime_core/utils/hardening_rt.so -lseccomp
```

Recovery relies on >=80% hardware fingerprint match and a saved recovery phrase.
Backup shards should be stored offline (e.g. USB).

## Documentation

See [docs/THREATS.md](docs/THREATS.md) and [docs/ARCH.md](docs/ARCH.md).
