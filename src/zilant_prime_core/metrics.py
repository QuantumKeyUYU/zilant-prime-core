# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

from __future__ import annotations

import os
import socket
import sys
import time
from contextlib import contextmanager
from functools import wraps
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from prometheus_client import Counter, Gauge, Histogram, generate_latest, start_http_server
from typing import Any, Callable, Iterator, cast

__all__ = ["metrics", "Metrics", "start_metrics_server", "trace_cli"]


class DynamicConsoleSpanExporter(ConsoleSpanExporter):
    def export(self, spans: list[trace.Span]) -> None:  # type: ignore[override]
        self.out = sys.stdout
        super().export(spans)


class Metrics:
    def __init__(self) -> None:
        self.requests_total: Counter = Counter("requests_total", "Total processed requests", ["name"])
        self.request_duration_seconds: Histogram = Histogram(
            "request_duration_seconds",
            "Request duration in seconds",
            ["name"],
        )
        self.command_duration_seconds: Histogram = Histogram(
            "command_duration_seconds",
            "CLI command duration in seconds",
            ["name"],
            buckets=[0.1, 0.5, 1, 5, 10],
        )
        self.files_processed_total: Counter = Counter(
            "files_processed_total",
            "Number of files processed",
        )
        self.encryption_duration_seconds: Histogram = Histogram(
            "encryption_duration_seconds",
            "Time spent encrypting/decrypting",
        )
        self.inflight_requests: Gauge = Gauge("inflight_requests", "In-flight requests", ["name"])

    @contextmanager
    def track(self, name: str) -> Iterator[None]:
        self.inflight_requests.labels(name).inc()
        with self.request_duration_seconds.labels(name).time():
            yield
        self.inflight_requests.labels(name).dec()
        self.requests_total.labels(name).inc()

    def record_cli(self, name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator to time CLI command execution."""

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                with self.command_duration_seconds.labels(name).time():
                    return func(*args, **kwargs)

            return wrapper

        return decorator

    def export(self) -> bytes:
        return cast(bytes, generate_latest())


metrics = Metrics()


def start_metrics_server(port: int = 9109) -> int:
    """Start Prometheus metrics HTTP server on *port*.

    If ``port`` is ``0`` then ``$ZILANT_METRICS_PORT`` is used if set, otherwise
    a random free port is chosen. The actual port is printed to ``stdout`` and
    returned.
    """
    if port == 0:
        env_port = os.getenv("ZILANT_METRICS_PORT")
        port = int(env_port) if env_port else 0
        if port == 0:
            with socket.socket() as s:
                s.bind(("", 0))
                port = s.getsockname()[1]
        print(port)
    start_http_server(port)
    return port


def _trace_enabled() -> bool:
    return os.getenv("ZILANT_TRACE") == "1"


def _ensure_tracer() -> trace.Tracer:
    if not isinstance(trace.get_tracer_provider(), TracerProvider):
        exporter = DynamicConsoleSpanExporter(
            formatter=lambda span: "[Span] " + " ".join(f"{k}={v}" for k, v in span.attributes.items()) + os.linesep,
        )
        provider = TracerProvider()
        provider.add_span_processor(SimpleSpanProcessor(exporter))
        trace.set_tracer_provider(provider)
    return trace.get_tracer("zilant.cli")


def trace_cli(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorate CLI command and emit OpenTelemetry span when enabled."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        if not _trace_enabled():
            return func

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            tracer = _ensure_tracer()
            with tracer.start_as_current_span(name) as span:
                span.set_attribute("cli.command", name)
                try:
                    result = func(*args, **kwargs)
                    span.set_attribute("success", True)
                    return result
                except Exception:
                    span.set_attribute("success", False)
                    raise
                finally:
                    span.set_attribute("duration_ms", int((time.perf_counter() - start) * 1000))

        return wrapper

    return decorator
