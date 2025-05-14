import os
import argon2.low_level as a2

from zilant_prime_core.utils.constants import DEFAULT_KEY_LENGTH, DEFAULT_SALT_LENGTH
from zilant_prime_core.crypto.g_new import G_new

# минимальное и максимальное значение памяти (KiB) для динамики
DEFAULT_MEMORY_MIN = 2 ** 15  # 32 MiB
DEFAULT_MEMORY_MAX = 2 ** 17  # 128 MiB
DEFAULT_TIME_MAX   = 5        # до 5 итераций

def generate_salt() -> bytes:
    return os.urandom(DEFAULT_SALT_LENGTH)

def derive_key(
    password: str | bytes,
    salt: bytes,
    key_length: int = DEFAULT_KEY_LENGTH
) -> bytes:
    """
    Статичный Argon2id KDF → key_length байт.
    """
    if isinstance(password, str):
        password = password.encode("utf-8")
    if not isinstance(password, (bytes, bytearray)):
        raise ValueError("Password must be bytes or string.")
    if not isinstance(salt, (bytes, bytearray)):
        raise ValueError("Salt must be bytes.")
    if not isinstance(key_length, int) or key_length <= 0:
        raise ValueError("Key length must be a positive integer.")

    return a2.hash_secret_raw(
        secret=password,
        salt=salt,
        time_cost=2,
        memory_cost=DEFAULT_MEMORY_MIN,
        parallelism=1,
        hash_len=key_length,
        type=a2.Type.ID,
    )

def derive_key_dynamic(
    password: str | bytes,
    salt: bytes,
    profile: float,
    key_length: int = DEFAULT_KEY_LENGTH,
    time_max: int = DEFAULT_TIME_MAX,
    mem_min: int = DEFAULT_MEMORY_MIN,
    mem_max: int = DEFAULT_MEMORY_MAX,
) -> bytes:
    """
    Динамично выбирает time_cost и memory_cost на основе G_new(profile):
      - G_new(profile) ∈ [-1.5,1.5] → нормируем в [0,1]
      - time_cost = 1 + int(norm*(time_max-1))
      - memory_cost = mem_min + int(norm*(mem_max-mem_min))
    """
    # Валидация входных параметров
    if not isinstance(password, (str, bytes)):
        raise ValueError("Password must be str or bytes.")
    if not isinstance(salt, (bytes, bytearray)):
        raise ValueError("Salt must be bytes.")
    # Проверка длины соли
    if len(salt) != DEFAULT_SALT_LENGTH:
        raise ValueError(f"Salt must be {DEFAULT_SALT_LENGTH} bytes long.")
    if not isinstance(profile, (int, float)):
        raise ValueError("Profile must be a number.")
    if not isinstance(key_length, int) or key_length <= 0:
        raise ValueError("Key length must be a positive integer.")
    if not isinstance(time_max, int) or time_max <= 0:
        raise ValueError("time_max must be a positive integer.")
    if not isinstance(mem_min, int) or mem_min <= 0:
        raise ValueError("mem_min must be a positive integer.")
    if not isinstance(mem_max, int) or mem_max < mem_min:
        raise ValueError("mem_max must be >= mem_min.")

    # Рассчитываем нормировочный коэффициент
    angle = abs(G_new(profile))            # ∈ [0,1.5]
    norm  = min(max(angle / 1.5, 0.0), 1.0)

    # Параметры Argon2
    time_cost   = 1 + int(norm * (time_max - 1))
    memory_cost = mem_min + int(norm * (mem_max - mem_min))

    # Подготавливаем пароль
    if isinstance(password, str):
        password = password.encode("utf-8")

    # Производим KDF
    return a2.hash_secret_raw(
        secret=password,
        salt=salt,
        time_cost=time_cost,
        memory_cost=memory_cost,
        parallelism=1,
        hash_len=key_length,
        type=a2.Type.ID,
    )
