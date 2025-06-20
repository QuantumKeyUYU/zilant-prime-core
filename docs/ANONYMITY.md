# Quantum Anonymity Layer

`QAL` creates a small group of post‑quantum signers. Messages are signed with
one of the group's secret keys and verified against every public key, providing
basic ring‑style anonymity.

```python
from pathlib import Path
from zilant_prime_core.utils import QAL

group = QAL(3, Path('/tmp/qal'))
sig = group.sign(b'msg', 0)
assert group.verify(b'msg', sig)
```

## Stealth Addresses

`QSSA` uses a hybrid post‑quantum KEM to generate ephemeral public keys for
receiving data. Each call to `generate_address()` returns a unique key pair.

```python
from zilant_prime_core.utils import QSSA

q = QSSA()
public, private = q.generate_address()
```
