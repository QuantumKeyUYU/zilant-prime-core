import os
import time
import urllib.request

os.environ.setdefault("ZILANT_TRACE", "1")

from zilant_prime_core.metrics import metrics, start_metrics_server


def test_metrics_server_autopick(capsys):
    os.environ.setdefault("ZILANT_TRACE", "1")
    port = start_metrics_server(0)
    captured = capsys.readouterr()
    if not port:
        port = int(captured.out.strip() or captured.err.strip())
    time.sleep(0.1)
    metrics.files_processed_total.inc()
    data = urllib.request.urlopen(f"http://localhost:{port}/metrics").read().decode()
    assert "command_duration_seconds" in data
