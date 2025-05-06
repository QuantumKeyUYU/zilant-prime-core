### KDF (Argon2id)

```python
from src.kdf import derive_key

key, salt = derive_key("my passphrase")
