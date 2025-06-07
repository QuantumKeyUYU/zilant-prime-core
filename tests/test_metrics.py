import time

from zilant_prime_core.metrics import metrics


def test_metrics_track():
    with metrics.track("test"):
        time.sleep(0.1)
    assert metrics.requests_total.labels("test")._value.get() == 1
    assert metrics.inflight_requests.labels("test")._value.get() == 0
    samples = metrics.request_duration_seconds.collect()[0].samples
    assert any(s.name.endswith("_count") and s.value == 1.0 for s in samples)
