import timeit

from zilant_prime_core import aead  # noqa: F401

setup = "from zilant_prime_core import aead; key=b'0'*32; data=b'x'*32"
stmt = "aead.encrypt(key, data)"


def main() -> None:
    t = min(timeit.repeat(stmt, setup=setup, number=1000, repeat=3))
    print(f"encrypt 1000x: {t:.4f}s")


if __name__ == "__main__":
    main()
