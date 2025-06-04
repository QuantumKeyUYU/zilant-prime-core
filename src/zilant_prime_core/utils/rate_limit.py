from __future__ import annotations

import time
from collections import deque

__all__ = ["RateLimiter"]


class RateLimiter:
    def __init__(self, key: str, max_calls: int, period: float) -> None:
        self.key = key
        self.max_calls = max_calls
        self.period = period
        self.calls: deque[float] = deque()

    def allow_request(self) -> bool:
        now = time.time()
        while self.calls and now - self.calls[0] > self.period:
            self.calls.popleft()
        if len(self.calls) >= self.max_calls:
            return False
        self.calls.append(now)
        return True
