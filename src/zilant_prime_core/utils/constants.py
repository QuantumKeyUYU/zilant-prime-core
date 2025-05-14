from struct import calcsize

# Для pack/unpack контейнера
MAGIC = b"ZILP"           # произвольное 4-байтовое «магическое» значение
VERSION = 1               # версия формата
HEADER_FMT = "!4sBIII"    # 4s: MAGIC, B: VERSION, I×3: длинны meta, proof, sig
HEADER_SIZE = calcsize(HEADER_FMT)

# Для AEAD/KDF
DEFAULT_KEY_LENGTH = 32
DEFAULT_NONCE_LENGTH = 12
DEFAULT_SALT_LENGTH = 16
