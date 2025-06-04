import time
from threading import Lock

__all__ = ["RateLimiter"]


class RateLimiter:
    """Simple token-bucket limiter."""

    def __init__(self, max_calls: int, period: float) -> None:
        self.max_calls = max_calls
        self.period = period
        self._lock = Lock()
        self._calls: list[float] = []

    def allow(self) -> bool:
        with self._lock:
            now = time.time()
            while self._calls and self._calls[0] <= now - self.period:
                self._calls.pop(0)
            if len(self._calls) < self.max_calls:
                self._calls.append(now)
                return True
            return False
