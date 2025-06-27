import timeit

from zilant_prime_core.container import pack_file  # noqa: F401

setup = "from zilant_prime_core.container import pack_file; open('tmp.txt','wb').write(b'x'*32)"
stmt = "pack_file('tmp.txt','tmp.zil',b'pw')"


def main() -> None:
    t = min(timeit.repeat(stmt, setup=setup, number=100, repeat=3))
    print(f"pack_file 100x: {t:.4f}s")


if __name__ == "__main__":
    main()
