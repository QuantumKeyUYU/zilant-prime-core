from struct import calcsize

# ─── Container header constants (not used in this minimal JSON approach) ───
MAGIC = b"ZILP"  # 4-byte magic
VERSION = 1  # 1-byte version
HEADER_FMT = "!4sBIII"  # for a more complex header if you want
HEADER_SIZE = calcsize(HEADER_FMT)

# ─── AEAD / KDF constants ───
DEFAULT_KEY_LENGTH = 32  # bytes
DEFAULT_NONCE_LENGTH = 12  # bytes
DEFAULT_SALT_LENGTH = 16  # bytes
