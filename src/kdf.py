import os
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id

def derive_key(passphrase: str) -> tuple[bytes, bytes]:
    # Генерируем соль 32 байта
    salt = os.urandom(32)

    # Настраиваем KDF: 32-байтовый ключ, 64 MiB памяти, 3 прохода, 1 lane
    kdf = Argon2id(
        salt=salt,
        length=32,
        memory_cost=64 * 1024,  # в Kibibytes: 64 MiB
        iterations=3,           # количество проходов (time_cost)
        lanes=1                 # степень параллелизма
    )

    # Деривация ключа
    key = kdf.derive(passphrase.encode("utf-8"))
    return key, salt
