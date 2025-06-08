from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from prometheus_client import Counter, Gauge, Histogram, generate_latest

__all__ = ["metrics", "Metrics"]


class Metrics:
    def __init__(self) -> None:
        self.requests_total: Counter = Counter("requests_total", "Total processed requests", ["name"])
        self.request_duration_seconds: Histogram = Histogram(
            "request_duration_seconds",
            "Request duration in seconds",
            ["name"],
        )
        self.inflight_requests: Gauge = Gauge("inflight_requests", "In-flight requests", ["name"])

    @contextmanager
    def track(self, name: str) -> Iterator[None]:
        self.inflight_requests.labels(name).inc()
        with self.request_duration_seconds.labels(name).time():
            yield
        self.inflight_requests.labels(name).dec()
        self.requests_total.labels(name).inc()

    def export(self) -> bytes:
        return generate_latest()


metrics = Metrics()
