# tests/test_kdf.py
import pytest
import time
import hashlib
import sys
import builtins # Add this import


# Function to ensure printing works during tests if default print doesn't
def debug_print(*args, **kwargs):
    """A simple print function that might work better in test environments."""
    # Attempt to use builtins.print directly
    builtins.print("DEBUG:", *args, **kwargs)


from zilant_prime_core.crypto.kdf import (
    derive_key, # Assuming derive_key is the main function to test
    generate_salt, # Assuming generate_salt is testable
    DEFAULT_SALT_LENGTH, # Import necessary constants
    DEFAULT_KEY_LENGTH, # Import necessary constants
    # Import Argon2 specific constants if needed for tests (Optional, depending on test needs)
    # DEFAULT_ARGON2_TIME_COST,
    # DEFAULT_ARGON2_MEMORY_COST,
    # DEFAULT_ARGON2_PARALLELISM
)

# REMOVE VDF imports as VDF tests should be in test_vdf.py
# from zilant_prime_core.vdf.vdf import generate_posw_sha256, verify_posw_sha256


# Basic test for derive_key (using Argon2id now)
def test_derive_key():
    password = b"mysecretpassword"
    salt = generate_salt()
    key = derive_key(password, salt)
    assert isinstance(key, bytes)
    assert len(key) == DEFAULT_KEY_LENGTH

    # Deriving key with same password and salt should produce the same key
    key_again = derive_key(password, salt)
    assert key == key_again

    # Deriving key with different password should produce a different key
    password_wrong = b"wrongpassword"
    key_wrong = derive_key(password_wrong, salt)
    assert key != key_wrong

    # Deriving key with different salt should produce a different key
    salt_different = generate_salt()
    key_different_salt = derive_key(password, salt_different)
    assert key != key_different_salt

# Test generate_salt
def test_generate_salt():
    salt1 = generate_salt()
    salt2 = generate_salt()
    assert isinstance(salt1, bytes)
    assert len(salt1) == DEFAULT_SALT_LENGTH
    assert salt1 != salt2 # Salts should be random and different

# REMOVE all VDF tests from here as they belong in test_vdf.py
# test_posw_correctness(), test_posw_correctness_edge_cases(),
# test_posw_invalid_input(), test_posw_verification_error(),
# test_posw_performance()