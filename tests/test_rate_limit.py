import time

from zilant_prime_core.utils.rate_limit import RateLimiter


def test_rate_limiter_basic():
    rl = RateLimiter("k", max_calls=3, period=1)
    assert rl.allow_request()
    assert rl.allow_request()
    assert rl.allow_request()
    assert not rl.allow_request()
    time.sleep(1.1)
    assert rl.allow_request()
