import pytest
import sys

if sys.platform == "win32":
    pytest.skip("mkfifo/sync unavailable on Windows", allow_module_level=True)

from zilant_prime_core.bench_zfs import bench_fs


def test_zilfs_bench() -> None:
    mb_s = bench_fs()
    assert mb_s > 5
