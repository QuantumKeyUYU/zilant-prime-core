import timeit

from zilant_prime_core.kdf import derive_key  # noqa: F401

setup = "from zilant_prime_core.kdf import derive_key; pwd=b'x'; salt=b'y'*16"
stmt = "derive_key(pwd, salt)"


def main() -> None:
    t = min(timeit.repeat(stmt, setup=setup, number=1000, repeat=3))
    print(f"derive_key 1000x: {t:.4f}s")


if __name__ == "__main__":
    main()
