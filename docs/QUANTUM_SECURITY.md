# Quantum Security Modules

Several helper classes showcase how quantum‑resistant primitives could be used
in practice. They are intentionally lightweight and are not full security
implementations.

## QuantumRA

Remote attestation of device information using post‑quantum signatures.

```python
from pathlib import Path
from zilant_prime_core.utils import QuantumRA

ra = QuantumRA(Path('/tmp/ra'))
signature = ra.attest(b'device-info')
assert ra.verify(b'device-info', signature)
```

## QVPN

A small Tor wrapper based on ``stem``.

```python
from zilant_prime_core.utils import QVPN

vpn = QVPN()
vpn.enable()
...
vpn.disable()
```

## ZKQP

Demonstrates zero‑knowledge style proofs built on `PQSign`.

```python
from pathlib import Path
from zilant_prime_core.utils import ZKQP

zk = ZKQP(Path('/tmp/zk'))
commit, proof = zk.prove(b'data')
assert zk.verify(b'data', commit, proof)
```
