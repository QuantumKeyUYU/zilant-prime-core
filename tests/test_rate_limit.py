import time

from zilant_prime_core.utils.rate_limit import RateLimiter


def test_rate_limiter_allows_and_blocks():
    rl = RateLimiter(max_calls=2, period=1.0)
    assert rl.allow() is True
    assert rl.allow() is True
    assert rl.allow() is False
    time.sleep(1.1)
    assert rl.allow() is True


def test_rate_limiter_thread_safety():
    rl = RateLimiter(max_calls=1, period=0.5)
    results: list[bool] = []

    def worker():
        results.append(rl.allow())

    import threading

    t1 = threading.Thread(target=worker)
    t2 = threading.Thread(target=worker)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    assert results.count(True) == 1
    assert results.count(False) == 1
